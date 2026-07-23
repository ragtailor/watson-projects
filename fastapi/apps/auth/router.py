"""auth 라우터 — 로그인/로그아웃/리프레시/콜백/JWKS.

auth_main.py가 prefix="/auth"로 include 한다.
회원가입 등은 이번 범위 밖이다.
"""

from __future__ import annotations

import logging
import os

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from auth import services
from auth.schemas import LoginRequest, RefreshRequest, TokenResponse
from auth.services import RefreshError, RefreshReuseError, OAuthError, IssuedTokens
from core.security import COOKIE_KWARGS, REFRESH_TOKEN_TTL_DAYS, build_jwks

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
_REFRESH_MAX_AGE = REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60

FRONTEND_REDIRECT_URL = os.getenv("FRONTEND_REDIRECT_URL", "http://localhost:3000").rstrip("/")


def _set_token_cookies(response: Response, tokens: IssuedTokens) -> None:
    response.set_cookie(
        ACCESS_COOKIE_NAME, tokens.access_token,
        max_age=tokens.expires_in, path="/", **COOKIE_KWARGS,
    )
    response.set_cookie(
        REFRESH_COOKIE_NAME, tokens.refresh_token,
        max_age=_REFRESH_MAX_AGE, path="/", **COOKIE_KWARGS,
    )


def _to_response(tokens: IssuedTokens) -> TokenResponse:
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
    )


@router.post("/login", response_model=TokenResponse, summary="OAuth 코드로 로그인 → 토큰 발급")
async def login(body: LoginRequest, response: Response) -> TokenResponse:
    try:
        tokens = await services.login(body.provider, body.code)
    except OAuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    _set_token_cookies(response, tokens)
    return _to_response(tokens)


@router.post("/logout", summary="세션 폐기(리프레시 패밀리 무효화) + 쿠키 제거")
async def logout(request: Request, response: Response) -> dict:
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    await services.logout(refresh_token)
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/")
    return {"ok": True}


@router.post("/refresh", response_model=TokenResponse, summary="리프레시 토큰 로테이션")
async def refresh(body: RefreshRequest, request: Request, response: Response) -> TokenResponse:
    token = body.refresh_token or request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="리프레시 토큰이 없습니다.")
    try:
        tokens = await services.refresh(token)
    except RefreshReuseError:
        # 재사용 감지 → 세션 전체 폐기됨. 쿠키도 제거하고 401.
        response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
        response.delete_cookie(REFRESH_COOKIE_NAME, path="/")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="세션이 폐기되었습니다.")
    except RefreshError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 리프레시 토큰입니다.")
    _set_token_cookies(response, tokens)
    return _to_response(tokens)


@router.get("/callback/{provider}", summary="OAuth 콜백(스텁) — 토큰 발급 후 프론트로 리다이렉트")
async def callback(provider: str, code: str | None = None, error: str | None = None) -> Response:
    from auth.rbac import Provider

    if error or not code:
        reason = error or "missing_code"
        return RedirectResponse(f"{FRONTEND_REDIRECT_URL}?auth=error&reason={reason}", status_code=302)
    try:
        prov = Provider(provider)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"지원하지 않는 프로바이더: {provider}")
    try:
        tokens = await services.login(prov, code)
    except OAuthError:
        return RedirectResponse(f"{FRONTEND_REDIRECT_URL}?auth=error&reason=oauth_error", status_code=302)
    resp = RedirectResponse(f"{FRONTEND_REDIRECT_URL}?auth=success", status_code=302)
    _set_token_cookies(resp, tokens)
    return resp


@router.get("/.well-known/jwks.json", summary="공개키 JWK Set (백엔드/외부 검증자용)")
async def jwks() -> JSONResponse:
    return JSONResponse(build_jwks())
