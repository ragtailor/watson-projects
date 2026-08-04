"""토큰 발급 오케스트레이션 — 카카오 OIDC 로그인, OAuth 로그인, 리프레시 로테이션.

이 모듈은 auth 컨테이너에서만 동작한다(개인키로 토큰을 발급).

세션은 플랫폼(mobile/web)별로 완전히 분리된다.
- 발급 토큰에 platform 클레임이 들어간다.
- 리프레시는 Redis 해시 `auth:session:{sub}`의 플랫폼 필드에 해시로만 저장된다.
- 요청 platform과 토큰 platform이 다르면 거부한다(교차 갱신·무효화 금지).

fastapi/pydantic에 의존하지 않는다. Redis 클라이언트와 DB는 지연 조회로 얻는다.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass

import jwt

from auth.oidc.kakao_verifier import KakaoIdentity, verify_id_token
from auth.rbac import Platform, Provider
from auth.store import refresh_store
from core import config
from core.security import (
    Role,
    TokenError,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)

# 플랫폼별 만료 정책 기본값. 모바일은 앱을 오래 켜 두므로 더 길게 잡는다.
_DEFAULT_TTL = {
    Platform.WEB: (30, 7),       # access 30분 / refresh 7일
    Platform.MOBILE: (60, 30),   # access 60분 / refresh 30일
}


class OAuthError(Exception):
    """OAuth 코드 교환 실패."""


class RefreshError(Exception):
    """리프레시 토큰이 유효하지 않음 → 401."""


class RefreshReuseError(RefreshError):
    """이미 로테이션된 리프레시 토큰의 재사용 → 해당 플랫폼 세션 폐기."""


class PlatformMismatchError(RefreshError):
    """요청 platform과 토큰의 platform 클레임이 다름 → 401."""


@dataclass(frozen=True)
class IssuedTokens:
    access_token: str
    refresh_token: str
    expires_in: int
    platform: str


def _ttl_for(platform: Platform) -> tuple[int, int]:
    """(access 분, refresh 일). 환경변수로 플랫폼별 조정이 가능하다."""
    access_default, refresh_default = _DEFAULT_TTL[platform]
    suffix = platform.value.upper()
    access_min = int(os.getenv(f"ACCESS_TTL_{suffix}_MIN", str(access_default)))
    refresh_days = int(os.getenv(f"REFRESH_TTL_{suffix}_DAYS", str(refresh_default)))
    return access_min, refresh_days


async def _resolve_user(identity: KakaoIdentity) -> str:
    """카카오 신원 → 우리 user_id. DB 접근을 지연 import로 감싼다(테스트 대체 지점)."""
    from auth.identity import resolve_user

    return await resolve_user(identity)


# --------------------------------------------------------------------------- #
# 카카오 OIDC 로그인
# --------------------------------------------------------------------------- #

async def kakao_login(id_token: str, platform: Platform, nonce: str) -> IssuedTokens:
    """카카오 id_token을 검증하고 자체 토큰을 발급한다.

    클라이언트가 보낸 프로필(email, nickname)은 받지 않는다. 검증된 클레임만 신뢰한다.
    KAPI(/v2/user/me)는 호출하지 않는다.
    """
    identity = await verify_id_token(id_token, nonce)
    sub = await _resolve_user(identity)
    return await _issue_pair(sub, [Role.USER.value], platform)


# --------------------------------------------------------------------------- #
# OAuth (스텁) — 실제 프로바이더 토큰 교환/프로필 조회는 이번 범위 밖.
# --------------------------------------------------------------------------- #

async def _exchange_oauth_code(provider: Provider, code: str) -> tuple[str, list[str]]:
    """인가 코드를 사용자 식별자(sub)와 역할로 교환한다.

    STUB: 실제 Google/Kakao/Naver/X 토큰 교환은 연동하지 않는다. code로부터
    결정적인 subject를 만들어 발급·검증·로테이션 흐름을 데모/테스트할 수 있게 한다.
    실제 연동 시 kingsman의 OAuth 어댑터로 profile을 조회해 sub를 채우면 된다.
    """
    if not code:
        raise OAuthError("인가 코드가 비어 있습니다.")
    subject = hashlib.sha256(f"{provider.value}:{code}".encode("utf-8")).hexdigest()[:32]
    sub = f"{provider.value}:{subject}"
    # 사용자별 역할 소스가 아직 없으므로 모든 OAuth 사용자를 USER로 부여한다.
    roles = [Role.USER.value]
    return sub, roles


# --------------------------------------------------------------------------- #
# 로그인 / 발급
# --------------------------------------------------------------------------- #

async def login(
    provider: Provider,
    code: str,
    platform: Platform = Platform.WEB,
) -> IssuedTokens:
    """인가 코드 로그인(브라우저 경로). 별도 지정이 없으면 web 세션이다."""
    sub, roles = await _exchange_oauth_code(provider, code)
    return await _issue_pair(sub, roles, platform)


async def _issue_pair(sub: str, roles: list[str], platform: Platform) -> IssuedTokens:
    access_min, refresh_days = _ttl_for(platform)
    access = create_access_token(
        sub=sub,
        roles=roles,
        aud=config.SERVICE_AUD,
        expires_min=access_min,
        platform=platform.value,
    )
    refresh = create_refresh_token(
        sub=sub,
        expires_days=refresh_days,
        platform=platform.value,
    )
    # 방금 스스로 만든 토큰의 jti만 읽으면 되므로 서명 검증(공개키)은 불필요.
    refresh_jti = jwt.decode(refresh, options={"verify_signature": False})["jti"]
    await refresh_store.save(
        sub=sub,
        platform=platform.value,
        token=refresh,
        jti=refresh_jti,
        ttl_sec=refresh_days * 24 * 60 * 60,
    )
    return IssuedTokens(
        access_token=access,
        refresh_token=refresh,
        expires_in=access_min * 60,
        platform=platform.value,
    )


# --------------------------------------------------------------------------- #
# 리프레시 로테이션 (재사용 감지 시 해당 플랫폼 세션 폐기)
# --------------------------------------------------------------------------- #

async def refresh(refresh_token: str, platform: Platform) -> IssuedTokens:
    try:
        payload = verify_refresh_token(refresh_token)
    except TokenError as exc:
        raise RefreshError(str(exc)) from exc

    # platform 클레임이 없는 토큰은 플랫폼 분리 도입 이전에 발급된 것이다.
    # web으로 간주하면 모바일 토큰이 웹 세션을 갱신할 수 있으므로 거부한다(1회 재로그인).
    if payload.platform is None:
        raise PlatformMismatchError("platform 정보가 없는 토큰입니다. 다시 로그인해 주세요.")
    if payload.platform != platform.value:
        raise PlatformMismatchError("토큰의 플랫폼과 요청 플랫폼이 다릅니다.")

    if not await refresh_store.matches(payload.sub, platform.value, refresh_token):
        # 서명·만료는 유효하지만 활성 슬롯과 다르다 → 이미 로테이션된 토큰의 재사용.
        # 폐기 범위는 해당 플랫폼 슬롯까지다. 여기서 전 플랫폼을 지우면 모바일 사고가
        # 웹 세션까지 끊어 플랫폼 분리 원칙을 스스로 어긴다.
        await refresh_store.revoke(payload.sub, platform.value)
        raise RefreshReuseError("리프레시 토큰 재사용이 감지되어 해당 세션을 폐기했습니다.")

    # 로테이션: 같은 슬롯을 새 토큰으로 덮어쓴다.
    # 역할은 스텁 단계에서 재조회 없이 USER로 유지한다.
    return await _issue_pair(payload.sub, [Role.USER.value], platform)


async def logout(refresh_token: str | None, platform: Platform) -> None:
    """해당 플랫폼 슬롯만 폐기한다. 다른 플랫폼 세션은 살아 있다."""
    if not refresh_token:
        return
    try:
        payload = verify_refresh_token(refresh_token)
    except TokenError:
        return
    if payload.platform is not None and payload.platform != platform.value:
        # 다른 플랫폼의 토큰으로 이 플랫폼 세션을 끊을 수 없다.
        return
    await refresh_store.revoke(payload.sub, platform.value)
