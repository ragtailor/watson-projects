from __future__ import annotations

import base64
import hashlib
import logging
import secrets

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from kingsman.adapter.outbound.repositories.user_repository import UserRepository
from kingsman.app.use_cases.oauth_login_interactor import OAuthLoginInteractor
from kingsman.dependencies.oauth_provider_registry import (
    FRONTEND_REDIRECT_URL,
    OAUTH_REDIRECT_BASE_URL,
    get_oauth_provider,
    get_state_guard,
    get_user_session,
)

logger = logging.getLogger(__name__)

oauth_router = APIRouter(prefix="/oauth", tags=["oauth"])

SESSION_COOKIE_NAME = "kingsman_session"


def _redirect_uri(provider: str) -> str:
    return f"{OAUTH_REDIRECT_BASE_URL}/api/kingsman/oauth/{provider}/callback"


@oauth_router.get("/{provider}/authorize", summary="소셜 로그인 시작 — 프로바이더 동의 화면으로 리다이렉트")
async def authorize(provider: str):
    adapter = get_oauth_provider(provider)
    guard = get_state_guard()

    code_verifier = None
    code_challenge = None
    if provider == "x":
        code_verifier = secrets.token_urlsafe(64)[:128]
        digest = hashlib.sha256(code_verifier.encode()).digest()
        code_challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")

    state = guard.issue(code_verifier or "")
    url = adapter.build_authorize_url(state, _redirect_uri(provider), code_challenge)
    return RedirectResponse(url, status_code=302)


@oauth_router.get("/{provider}/callback", summary="프로바이더 콜백 — 로그인 완료 후 세션 발급")
async def callback(
    provider: str,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    if error or not code or not state:
        reason = error or "missing_code"
        return RedirectResponse(f"{FRONTEND_REDIRECT_URL}?auth=error&reason={reason}", status_code=302)

    adapter = get_oauth_provider(provider)
    guard = get_state_guard()
    code_verifier = guard.verify(state)
    if code_verifier is None:
        return RedirectResponse(f"{FRONTEND_REDIRECT_URL}?auth=error&reason=invalid_state", status_code=302)

    try:
        profile = await adapter.fetch_profile(code, _redirect_uri(provider), code_verifier or None)
    except Exception:
        logger.exception("[oauth_router] provider=%s 프로필 조회 실패", provider)
        return RedirectResponse(f"{FRONTEND_REDIRECT_URL}?auth=error&reason=provider_error", status_code=302)

    use_case = OAuthLoginInteractor(users=UserRepository(session=db))
    result = await use_case.login_with_profile(profile)

    session = get_user_session()
    token = session.issue(result.user_id)

    resp = RedirectResponse(f"{FRONTEND_REDIRECT_URL}?auth=success", status_code=302)
    resp.set_cookie(
        SESSION_COOKIE_NAME, token,
        max_age=12 * 60 * 60, path="/",
        httponly=True, secure=True, samesite="lax",
    )
    return resp
