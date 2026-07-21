from __future__ import annotations

from abc import ABC, abstractmethod

from kingsman.app.dtos.oauth_dto import OAuthProfile


class OAuthProviderPort(ABC):
    """소셜 로그인 프로바이더(구글/네이버/카카오/X) 어댑터가 구현하는 출력 포트."""

    @abstractmethod
    def build_authorize_url(self, state: str, redirect_uri: str, code_challenge: str | None = None) -> str:
        """프로바이더의 인증 동의 화면 URL을 생성한다."""
        pass

    @abstractmethod
    async def fetch_profile(self, code: str, redirect_uri: str, code_verifier: str | None = None) -> OAuthProfile:
        """authorization code를 토큰으로 교환하고, 프로필을 조회해 반환한다."""
        pass
