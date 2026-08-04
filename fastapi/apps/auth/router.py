"""auth 라우터 — 로그인/로그아웃/리프레시/콜백/JWKS.

auth_main.py가 prefix="/auth"로 include 한다.
회원가입 등은 이번 범위 밖이다.

토큰 전달 방식은 플랫폼에 따라 다르다.
- web: 쿠키(HttpOnly) + 응답 body
- mobile: 응답 body만. 앱은 쿠키 저장소가 아니라 보안 저장소를 쓴다.
"""

from __future__ import annotations

import logging
import os

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from auth import services
from auth.oidc.kakao_verifier import KakaoKeyUnavailable, KakaoVerifyError
from auth.rbac import Platform
from auth.schemas import (
    KakaoLoginRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenResponse,
)
from auth.services import (
    IssuedTokens,
    OAuthError,
    RefreshError,
    RefreshReuseError,
)
from core.security import COOKIE_KWARGS, REFRESH_TOKEN_TTL_DAYS, build_jwks

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
_REFRESH_MAX_AGE = REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60

FRONTEND_REDIRECT_URL = os.getenv("FRONTEND_REDIRECT_URL", "http://localhost:3000").rstrip("/")


def _set_token_cookies(response: Response, tokens: IssuedTokens) -> None:
    """web 세션만 쿠키를 받는다. 모바일은 body로만 전달한다."""
    if tokens.platform != Platform.WEB.value:
        return
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
        platform=Platform(tokens.platform),
    )


@router.post("/kakao/login", response_model=TokenResponse, summary="카카오 id_token으로 로그인")
async def kakao_login(body: KakaoLoginRequest, response: Response) -> TokenResponse:
    try:
        tokens = await services.kakao_login(body.id_token, body.platform, body.nonce)
    except KakaoVerifyError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except KakaoKeyUnavailable as exc:
        # 토큰 문제가 아니라 서버가 카카오 공개키를 확보하지 못한 상황이다.
        logger.warning("[auth] 카카오 공개키 확보 실패 — %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="카카오 인증 서버와 통신하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        )
    _set_token_cookies(response, tokens)
    return _to_response(tokens)


@router.post("/login", response_model=TokenResponse, summary="OAuth 코드로 로그인 → 토큰 발급")
async def login(body: LoginRequest, response: Response) -> TokenResponse:
    try:
        tokens = await services.login(body.provider, body.code, body.platform)
    except OAuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    _set_token_cookies(response, tokens)
    return _to_response(tokens)


@router.post("/logout", summary="해당 플랫폼 세션만 폐기 + 쿠키 제거")
async def logout(body: LogoutRequest, request: Request, response: Response) -> dict:
    token = body.refresh_token or request.cookies.get(REFRESH_COOKIE_NAME)
    await services.logout(token, body.platform)
    if body.platform == Platform.WEB:
        response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
        response.delete_cookie(REFRESH_COOKIE_NAME, path="/")
    return {"ok": True}


@router.post("/refresh", response_model=TokenResponse, summary="리프레시 토큰 로테이션")
async def refresh(body: RefreshRequest, request: Request, response: Response) -> TokenResponse:
    token = body.refresh_token or request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="리프레시 토큰이 없습니다.")
    try:
        tokens = await services.refresh(token, body.platform)
    except RefreshReuseError:
        # 재사용 감지 → 해당 플랫폼 세션 폐기됨. 쿠키도 제거하고 401.
        if body.platform == Platform.WEB:
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
        # 브라우저 콜백이므로 언제나 web 세션이다.
        tokens = await services.login(prov, code, Platform.WEB)
    except OAuthError:
        return RedirectResponse(f"{FRONTEND_REDIRECT_URL}?auth=error&reason=oauth_error", status_code=302)
    resp = RedirectResponse(f"{FRONTEND_REDIRECT_URL}?auth=success", status_code=302)
    _set_token_cookies(resp, tokens)
    return resp


@router.get("/.well-known/jwks.json", summary="공개키 JWK Set (백엔드/외부 검증자용)")
async def jwks() -> JSONResponse:
    return JSONResponse(build_jwks())
