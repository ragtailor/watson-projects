"""보안 프리미티브 — JWT(RS256) 발급/검증, JWKS, RBAC 어휘.

키 체계는 RS256 비대칭이다.
- 발급부(create_*_token)는 auth 컨테이너 전용이며 JWT_PRIVATE_KEY가 필요하다.
- 검증부(verify_*)는 모든 컨테이너 공용이며 JWT_PUBLIC_KEY만 있으면 된다.
- 검증 경로는 개인키를 절대 참조하지 않는다.

이 모듈은 fastapi/redis에 의존하지 않는다(검증이 어디서든 가능하도록).
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
from dataclasses import dataclass
from enum import StrEnum

import jwt

from core import config

# 검증 시 허용하는 알고리즘은 리터럴로 하드코딩한다(절대 규칙).
# 환경변수·설정으로 빼지 않는다. alg=none / HS256 강제 토큰을 원천 차단한다.
_ALLOWED_ALGORITHMS = ["RS256"]

ACCESS_TOKEN_DEFAULT_MIN = 10
REFRESH_TOKEN_TTL_DAYS = 14

# auth 발급 시 쿠키에 사용하는 공통 속성.
COOKIE_KWARGS = dict(
    domain=".ragtailor.com",
    secure=True,
    httponly=True,
    samesite="lax",
)


class Role(StrEnum):
    """RBAC 역할. RoleChecker와 access token의 roles 클레임에서 공용으로 쓴다.

    core에 두는 이유: 백엔드(core.dependencies)와 auth(apps.auth.rbac)가
    모두 참조해야 하며, core가 apps.auth를 import하면 안 되기 때문이다.
    """

    ADMIN = "admin"
    USER = "user"


class TokenError(Exception):
    """토큰 검증 실패(만료·서명 변조·aud 불일치·형식 오류 등)."""


@dataclass(frozen=True)
class TokenPayload:
    sub: str
    roles: list[str]
    aud: str
    exp: int
    iat: int
    jti: str


@dataclass(frozen=True)
class RefreshPayload:
    sub: str
    exp: int
    iat: int
    jti: str


# --------------------------------------------------------------------------- #
# 발급부 — auth 컨테이너 전용 (JWT_PRIVATE_KEY 필요, 호출 시점에 키를 읽는다)
# --------------------------------------------------------------------------- #

def create_access_token(
    sub: str,
    roles: list[str],
    aud: str,
    expires_min: int = ACCESS_TOKEN_DEFAULT_MIN,
) -> str:
    private_key = config.get_jwt_private_key()
    now = int(time.time())
    payload = {
        "sub": sub,
        "roles": list(roles),
        "aud": aud,
        "iat": now,
        "exp": now + expires_min * 60,
        "jti": secrets.token_urlsafe(16),
    }
    headers = {"kid": _kid_from_private_key(private_key)}
    return jwt.encode(payload, private_key, algorithm="RS256", headers=headers)


def create_refresh_token(sub: str) -> str:
    private_key = config.get_jwt_private_key()
    now = int(time.time())
    payload = {
        "sub": sub,
        "iat": now,
        "exp": now + REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60,
        "jti": secrets.token_urlsafe(16),
        "typ": "refresh",
    }
    headers = {"kid": _kid_from_private_key(private_key)}
    return jwt.encode(payload, private_key, algorithm="RS256", headers=headers)


# --------------------------------------------------------------------------- #
# 검증부 — 모든 컨테이너 공용 (JWT_PUBLIC_KEY만 필요)
# --------------------------------------------------------------------------- #

def verify_token(token: str, aud: str) -> TokenPayload:
    public_key = config.get_jwt_public_key()
    try:
        claims = jwt.decode(token, public_key, algorithms=_ALLOWED_ALGORITHMS, audience=aud)
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc
    try:
        return TokenPayload(
            sub=claims["sub"],
            roles=list(claims.get("roles", [])),
            aud=claims["aud"],
            exp=int(claims["exp"]),
            iat=int(claims["iat"]),
            jti=claims["jti"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise TokenError(f"토큰 클레임이 올바르지 않습니다: {exc}") from exc


def verify_refresh_token(token: str) -> RefreshPayload:
    public_key = config.get_jwt_public_key()
    try:
        # 리프레시 토큰에는 aud를 넣지 않으므로 audience 검증을 요구하지 않는다.
        claims = jwt.decode(token, public_key, algorithms=_ALLOWED_ALGORITHMS)
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc
    if claims.get("typ") != "refresh":
        raise TokenError("리프레시 토큰이 아닙니다.")
    try:
        return RefreshPayload(
            sub=claims["sub"],
            exp=int(claims["exp"]),
            iat=int(claims["iat"]),
            jti=claims["jti"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise TokenError(f"리프레시 토큰 클레임이 올바르지 않습니다: {exc}") from exc


# --------------------------------------------------------------------------- #
# JWKS — 공개키를 JWK(kid 포함)로 노출. 백엔드/외부 검증자가 사용한다.
# --------------------------------------------------------------------------- #

def build_jwks() -> dict:
    """auth 컨테이너에서 개인키로부터 공개 파라미터를 유도해 JWKS를 만든다.

    JWKS 자체는 공개 정보이며, auth는 개인키를 이미 갖고 있으므로 공개키를 별도로
    주입받지 않아도 된다.
    """
    private_key = config.get_jwt_private_key()
    n_b64, e_b64 = _public_numbers_b64(private_key)
    kid = _jwk_thumbprint(n_b64, e_b64)
    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": kid,
                "n": n_b64,
                "e": e_b64,
            }
        ]
    }


# --------------------------------------------------------------------------- #
# 해싱 — auth 전용 (bcrypt). 지연 import로 검증 경로/백엔드 import를 가볍게 유지.
# --------------------------------------------------------------------------- #

def hash_password(raw: str) -> str:
    import bcrypt

    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(raw: str, hashed: str) -> bool:
    import bcrypt

    return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))


# --------------------------------------------------------------------------- #
# 내부 헬퍼
# --------------------------------------------------------------------------- #

def _public_numbers_b64(private_pem: str) -> tuple[str, str]:
    from cryptography.hazmat.primitives.serialization import load_pem_private_key

    key = load_pem_private_key(private_pem.encode("utf-8"), password=None)
    numbers = key.public_key().public_numbers()  # type: ignore[attr-defined]
    return _b64url_uint(numbers.n), _b64url_uint(numbers.e)


def _kid_from_private_key(private_pem: str) -> str:
    n_b64, e_b64 = _public_numbers_b64(private_pem)
    return _jwk_thumbprint(n_b64, e_b64)


def _jwk_thumbprint(n_b64: str, e_b64: str) -> str:
    """RFC 7638 JWK thumbprint. 토큰 헤더 kid와 JWKS kid가 항상 일치하도록 유도한다."""
    canonical = json.dumps(
        {"e": e_b64, "kty": "RSA", "n": n_b64},
        separators=(",", ":"),
        sort_keys=True,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _b64url_uint(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
