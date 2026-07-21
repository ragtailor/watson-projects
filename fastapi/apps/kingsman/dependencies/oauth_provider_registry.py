import os

from fastapi import HTTPException

from kingsman.adapter.outbound.oauth.google_oauth_adapter import GoogleOAuthAdapter
from kingsman.adapter.outbound.oauth.kakao_oauth_adapter import KakaoOAuthAdapter
from kingsman.adapter.outbound.oauth.naver_oauth_adapter import NaverOAuthAdapter
from kingsman.adapter.outbound.oauth.x_oauth_adapter import XOAuthAdapter
from kingsman.adapter.outbound.session.oauth_state_guard import OAuthStateGuard
from kingsman.adapter.outbound.session.signed_cookie_session_adapter import SignedCookieSessionAdapter
from kingsman.app.ports.output.oauth_provider_port import OAuthProviderPort
from kingsman.app.ports.output.user_session_port import UserSessionPort

OAUTH_REDIRECT_BASE_URL = os.getenv("OAUTH_REDIRECT_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
FRONTEND_REDIRECT_URL = os.getenv("FRONTEND_REDIRECT_URL", "http://localhost:3000").rstrip("/")
_USER_SESSION_SECRET = os.getenv("USER_SESSION_SECRET", "")

_PROVIDERS: dict[str, OAuthProviderPort] = {
    "google": GoogleOAuthAdapter(
        client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
    ),
    "naver": NaverOAuthAdapter(
        client_id=os.getenv("NAVER_CLIENT_ID", ""),
        client_secret=os.getenv("NAVER_CLIENT_SECRET", ""),
    ),
    "kakao": KakaoOAuthAdapter(
        client_id=os.getenv("KAKAO_CLIENT_ID", ""),
        client_secret=os.getenv("KAKAO_CLIENT_SECRET", ""),
    ),
    "x": XOAuthAdapter(
        client_id=os.getenv("X_CLIENT_ID", ""),
        client_secret=os.getenv("X_CLIENT_SECRET", ""),
    ),
}


def get_oauth_provider(provider: str) -> OAuthProviderPort:
    adapter = _PROVIDERS.get(provider)
    if adapter is None:
        raise HTTPException(status_code=404, detail=f"지원하지 않는 로그인 프로바이더입니다: {provider}")
    return adapter


def get_state_guard() -> OAuthStateGuard:
    return OAuthStateGuard(secret=_USER_SESSION_SECRET)


def get_user_session() -> UserSessionPort:
    return SignedCookieSessionAdapter(secret=_USER_SESSION_SECRET)
