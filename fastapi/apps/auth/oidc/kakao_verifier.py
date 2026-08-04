"""카카오 OIDC id_token 검증 — 서명(JWKS) + iss/aud/exp/nonce.

클라이언트(Flutter/웹)가 카카오 SDK로 받은 id_token을 서버가 직접 검증한다.
기본 로그인 경로에서 KAPI(/v2/user/me)를 호출하지 않는다 — 필요한 값은 전부
id_token 클레임에 있다.

서명 검증 없이 payload만 디코드해 쓰는 경로는 두지 않는다.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import dataclass

import httpx
import jwt
from jwt.algorithms import RSAAlgorithm

# 검증 허용 알고리즘은 리터럴로 고정한다(core.security와 같은 규칙).
_ALLOWED_ALGORITHMS = ["RS256"]

_DEFAULT_ISSUER = "https://kauth.kakao.com"
_DEFAULT_CONFIG_URL = "https://kauth.kakao.com/.well-known/openid-configuration"
_DEFAULT_CACHE_TTL_SEC = 6 * 60 * 60

_HTTP_TIMEOUT_SEC = 5.0


class KakaoVerifyError(Exception):
    """id_token이 유효하지 않다 → 401."""


class KakaoKeyUnavailable(Exception):
    """카카오 공개키를 확보하지 못했다(서버 사정) → 503.

    토큰 문제와 구분한다. 이걸 401로 뭉개면 클라이언트가 멀쩡한 세션을 버린다.
    """


@dataclass(frozen=True)
class KakaoIdentity:
    """검증된 id_token 클레임에서만 만들어지는 신원."""

    sub: str          # 카카오 회원번호. 문자열로 다룬다(정수 캐스팅 금지).
    email: str | None  # 동의하지 않으면 없다.
    nickname: str | None


def _issuer() -> str:
    return os.getenv("KAKAO_OIDC_ISSUER", _DEFAULT_ISSUER)


def _config_url() -> str:
    return os.getenv("KAKAO_OIDC_CONFIG_URL", _DEFAULT_CONFIG_URL)


def _cache_ttl() -> int:
    return int(os.getenv("KAKAO_OIDC_CACHE_TTL_SECONDS", str(_DEFAULT_CACHE_TTL_SEC)))


def _audience() -> str:
    """id_token의 aud — 카카오 앱의 REST API 키.

    모바일과 웹이 같은 카카오 앱을 쓰므로 값은 하나다.
    """
    client_id = os.getenv("KAKAO_CLIENT_ID")
    if not client_id:
        raise KakaoKeyUnavailable("KAKAO_CLIENT_ID가 설정되지 않았습니다.")
    return client_id


# --------------------------------------------------------------------------- #
# JWKS / openid-configuration 캐시
#
# 매 요청 조회하지 않는다. kid가 캐시에 없을 때만 강제 갱신해 키 롤오버에 대응한다.
# 워커별 인메모리 캐시로 충분하다(워커당 TTL마다 1회 조회).
# --------------------------------------------------------------------------- #

_keys: dict[str, object] = {}
_jwks_uri: str | None = None
_expires_at: float = 0.0
_lock = asyncio.Lock()


def reset_cache() -> None:
    """캐시를 비운다. 테스트와 운영 중 수동 초기화에 쓴다."""
    global _keys, _jwks_uri, _expires_at
    _keys = {}
    _jwks_uri = None
    _expires_at = 0.0


async def _fetch_json(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url, timeout=_HTTP_TIMEOUT_SEC)
    response.raise_for_status()
    return response.json()


async def _refresh_keys() -> None:
    """openid-configuration → jwks_uri → 공개키 목록을 다시 읽는다.

    실패해도 기존 캐시를 지우지 않는다(외부 장애 시 캐시로 버티기 위해).
    """
    global _keys, _jwks_uri, _expires_at

    async with httpx.AsyncClient() as client:
        jwks_uri = _jwks_uri
        if jwks_uri is None:
            config = await _fetch_json(client, _config_url())
            jwks_uri = config.get("jwks_uri")
            if not jwks_uri:
                raise KakaoKeyUnavailable("openid-configuration에 jwks_uri가 없습니다.")
        jwks = await _fetch_json(client, jwks_uri)

    keys: dict[str, object] = {}
    for jwk in jwks.get("keys", []):
        kid = jwk.get("kid")
        if kid:
            keys[kid] = RSAAlgorithm.from_jwk(json.dumps(jwk))

    if not keys:
        raise KakaoKeyUnavailable("카카오 JWKS가 비어 있습니다.")

    _keys = keys
    _jwks_uri = jwks_uri
    _expires_at = time.time() + _cache_ttl()


async def _public_key_for(kid: str) -> object:
    """kid에 해당하는 공개키. 캐시 미스일 때만 갱신한다."""
    async with _lock:
        expired = time.time() >= _expires_at
        if kid in _keys and not expired:
            return _keys[kid]

        try:
            await _refresh_keys()
        except KakaoKeyUnavailable:
            raise
        except Exception as exc:  # 네트워크·HTTP 오류
            # 갱신에 실패해도 캐시에 키가 있으면 그걸로 버틴다.
            if kid in _keys:
                return _keys[kid]
            raise KakaoKeyUnavailable(f"카카오 공개키를 가져오지 못했습니다: {exc}") from exc

        if kid not in _keys:
            # 갱신 후에도 없다면 토큰 쪽 문제다.
            raise KakaoVerifyError("id_token의 kid에 해당하는 카카오 공개키가 없습니다.")
        return _keys[kid]


# --------------------------------------------------------------------------- #
# 검증
# --------------------------------------------------------------------------- #

async def verify_id_token(id_token: str, nonce: str) -> KakaoIdentity:
    """id_token의 서명과 iss/aud/exp/nonce를 검증하고 신원을 반환한다.

    실패는 KakaoVerifyError(401), 공개키 확보 실패는 KakaoKeyUnavailable(503).
    """
    audience = _audience()

    try:
        header = jwt.get_unverified_header(id_token)
    except jwt.PyJWTError as exc:
        raise KakaoVerifyError(f"id_token 형식이 올바르지 않습니다: {exc}") from exc

    kid = header.get("kid")
    if not kid:
        raise KakaoVerifyError("id_token 헤더에 kid가 없습니다.")

    public_key = await _public_key_for(kid)

    try:
        claims = jwt.decode(
            id_token,
            public_key,
            algorithms=_ALLOWED_ALGORITHMS,
            audience=audience,
            issuer=_issuer(),
        )
    except jwt.PyJWTError as exc:
        raise KakaoVerifyError(f"id_token 검증에 실패했습니다: {exc}") from exc

    # nonce는 클라이언트가 만들어 카카오와 서버 양쪽에 보낸 값이다. 재생 공격을 막는다.
    if claims.get("nonce") != nonce:
        raise KakaoVerifyError("nonce가 일치하지 않습니다.")

    sub = claims.get("sub")
    if not sub:
        raise KakaoVerifyError("id_token에 sub가 없습니다.")

    return KakaoIdentity(
        sub=str(sub),
        email=claims.get("email"),
        nickname=claims.get("nickname"),
    )
