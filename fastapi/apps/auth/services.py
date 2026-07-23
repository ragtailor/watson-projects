"""토큰 발급 오케스트레이션 — OAuth 로그인, 리프레시 로테이션.

이 모듈은 auth 컨테이너에서만 동작한다(개인키로 토큰을 발급).
리프레시 토큰은 Redis(totem)에 저장하고 로테이션 방식으로 운용하며,
재사용이 감지되면 해당 사용자의 세션 전체를 폐기한다.

fastapi/pydantic에 의존하지 않는다. Redis 클라이언트는 지연 조회로 얻는다.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import jwt

from auth.rbac import Provider
from core import config
from core.security import (
    ACCESS_TOKEN_DEFAULT_MIN,
    Role,
    TokenError,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)

# Redis 키 네임스페이스.
_REFRESH_KEY = "auth:refresh:{jti}"          # 값=sub, 활성 리프레시 토큰
_FAMILY_KEY = "auth:refresh:family:{sub}"    # 값=활성 jti들의 SET (세션 패밀리)
_REFRESH_TTL_SEC = 14 * 24 * 60 * 60


class OAuthError(Exception):
    """OAuth 코드 교환 실패."""


class RefreshError(Exception):
    """리프레시 토큰이 유효하지 않음 → 401."""


class RefreshReuseError(RefreshError):
    """이미 로테이션된 리프레시 토큰의 재사용 → 세션 전체 폐기."""


@dataclass(frozen=True)
class IssuedTokens:
    access_token: str
    refresh_token: str
    expires_in: int


def _redis():
    """totem Redis 클라이언트를 지연 조회한다(모듈 import를 가볍게 유지)."""
    from core.matrix.totem_redis_cache_manager import get_client

    return get_client()


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

async def login(provider: Provider, code: str) -> IssuedTokens:
    sub, roles = await _exchange_oauth_code(provider, code)
    return await _issue_pair(sub, roles)


async def _issue_pair(sub: str, roles: list[str]) -> IssuedTokens:
    access = create_access_token(sub=sub, roles=roles, aud=config.SERVICE_AUD)
    refresh = create_refresh_token(sub=sub)
    # 방금 스스로 만든 토큰의 jti만 읽으면 되므로 서명 검증(공개키)은 불필요.
    refresh_jti = jwt.decode(refresh, options={"verify_signature": False})["jti"]
    await _register_refresh(sub, refresh_jti)
    return IssuedTokens(
        access_token=access,
        refresh_token=refresh,
        expires_in=ACCESS_TOKEN_DEFAULT_MIN * 60,
    )


# --------------------------------------------------------------------------- #
# 리프레시 로테이션 (재사용 감지 시 세션 전체 폐기)
# --------------------------------------------------------------------------- #

async def refresh(refresh_token: str) -> IssuedTokens:
    try:
        payload = verify_refresh_token(refresh_token)
    except TokenError as exc:
        raise RefreshError(str(exc)) from exc

    client = _redis()
    active = await client.get(_REFRESH_KEY.format(jti=payload.jti))
    if not active:
        # 서명·만료는 유효하지만 저장소에 없다 → 이미 로테이션된 토큰의 재사용.
        await _revoke_family(payload.sub)
        raise RefreshReuseError("리프레시 토큰 재사용이 감지되어 세션 전체를 폐기했습니다.")

    # 로테이션: 기존 jti 폐기 후 새 쌍 발급.
    await _drop_refresh(payload.sub, payload.jti)
    # 역할은 스텁 단계에서 재조회 없이 USER로 유지한다.
    return await _issue_pair(payload.sub, [Role.USER.value])


async def logout(refresh_token: str | None) -> None:
    """리프레시 토큰이 주어지면 해당 사용자의 세션 패밀리를 폐기한다."""
    if not refresh_token:
        return
    try:
        payload = verify_refresh_token(refresh_token)
    except TokenError:
        return
    await _revoke_family(payload.sub)


# --------------------------------------------------------------------------- #
# Redis 조작
# --------------------------------------------------------------------------- #

async def _register_refresh(sub: str, jti: str) -> None:
    client = _redis()
    await client.set(_REFRESH_KEY.format(jti=jti), sub, ex=_REFRESH_TTL_SEC)
    family = _FAMILY_KEY.format(sub=sub)
    await client.sadd(family, jti)
    await client.expire(family, _REFRESH_TTL_SEC)


async def _drop_refresh(sub: str, jti: str) -> None:
    client = _redis()
    await client.delete(_REFRESH_KEY.format(jti=jti))
    await client.srem(_FAMILY_KEY.format(sub=sub), jti)


async def _revoke_family(sub: str) -> None:
    client = _redis()
    family = _FAMILY_KEY.format(sub=sub)
    members = await client.smembers(family)
    for jti in members or []:
        await client.delete(_REFRESH_KEY.format(jti=jti))
    await client.delete(family)
