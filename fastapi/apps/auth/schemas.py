"""auth 라우터 Pydantic 스키마."""

from __future__ import annotations

from pydantic import BaseModel, Field

from auth.rbac import Platform, Provider


class LoginRequest(BaseModel):
    """OAuth 인가 코드로 로그인. (프로바이더 코드 교환은 이번 범위에서 스텁)"""

    provider: Provider
    code: str = Field(..., min_length=1)
    platform: Platform = Platform.WEB


class KakaoLoginRequest(BaseModel):
    """카카오 SDK가 발급한 id_token으로 로그인.

    프로필(email, nickname)은 받지 않는다 — 클라이언트가 보낸 사용자 정보는 신뢰하지 않고
    검증된 id_token 클레임만 쓴다. nonce는 재생 공격 방지를 위해 필수다.
    """

    id_token: str = Field(..., min_length=1)
    platform: Platform
    nonce: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    """리프레시 토큰. 쿠키가 없을 때(모바일) 바디로도 받을 수 있다."""

    refresh_token: str | None = None
    platform: Platform


class LogoutRequest(BaseModel):
    """플랫폼 슬롯 하나만 폐기한다."""

    refresh_token: str | None = None
    platform: Platform


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    platform: Platform
