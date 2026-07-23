"""auth 라우터 Pydantic 스키마."""

from __future__ import annotations

from pydantic import BaseModel, Field

from auth.rbac import Provider


class LoginRequest(BaseModel):
    """OAuth 인가 코드로 로그인. (프로바이더 코드 교환은 이번 범위에서 스텁)"""

    provider: Provider
    code: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    """리프레시 토큰. 쿠키가 없을 때 바디로도 받을 수 있다."""

    refresh_token: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
