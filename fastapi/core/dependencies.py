"""FastAPI 의존성 — 인증/인가 진입점.

백엔드(영화 앱)가 인증을 위해 쓸 수 있는 유일한 접점이다.
apps.auth를 절대 import하지 않는다(발급부와 검증부를 물리적으로 분리).
"""

from __future__ import annotations

import logging

from fastapi import Depends, HTTPException, Request, status

from core import config
from core.security import Role, TokenError, TokenPayload, verify_token

logger = logging.getLogger(__name__)

# auth 컨테이너가 발급 시 사용하는 쿠키 이름과 일치해야 한다.
ACCESS_COOKIE_NAME = "access_token"

# Redis 블랙리스트 키 네임스페이스 (jti 기준 즉시 차단).
_BLACKLIST_KEY = "auth:blacklist:{jti}"

__all__ = ["Role", "TokenPayload", "get_current_user", "RoleChecker"]


def _extract_token(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip() or None
    cookie = request.cookies.get(ACCESS_COOKIE_NAME)
    return cookie or None


async def _is_blacklisted(jti: str) -> bool:
    """jti가 즉시 차단 목록에 있는지 확인한다.

    Redis를 사용할 수 없으면(예: REDIS_URL 미설정) 차단 목록을 건너뛴다(fail-open).
    토큰 서명 검증은 이미 통과한 상태이므로, 인프라 미비로 정상 토큰을 막지 않는다.
    """
    try:
        from core.matrix.totem_redis_cache_manager import get_client

        client = get_client()
        return bool(await client.get(_BLACKLIST_KEY.format(jti=jti)))
    except Exception:  # noqa: BLE001 - Redis 부재/장애는 fail-open 처리
        logger.debug("[dependencies] 블랙리스트 조회 생략(Redis 미가용)")
        return False


async def get_current_user(request: Request) -> TokenPayload:
    token = _extract_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 없습니다.",
        )
    try:
        payload = verify_token(token, aud=config.SERVICE_AUD)
    except TokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
        )
    if await _is_blacklisted(payload.jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="차단된 세션입니다.",
        )
    return payload


class RoleChecker:
    """지정한 역할 중 하나 이상을 가진 사용자만 통과시킨다.

    사용 예:
        dependencies=[Depends(RoleChecker(Role.USER))]
    """

    def __init__(self, *allowed: Role) -> None:
        self._allowed = {role.value for role in allowed}

    def __call__(self, user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if not self._allowed:
            return user
        if not (set(user.roles) & self._allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 부족합니다.",
            )
        return user
