from __future__ import annotations

from abc import ABC, abstractmethod

from kingsman.app.dtos.oauth_dto import OAuthLoginResult, OAuthProfile


class OAuthLoginUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/oauth_router.py 와 대응."""

    @abstractmethod
    async def login_with_profile(self, profile: OAuthProfile) -> OAuthLoginResult:
        """OAuth 프로필로 기존 사용자를 조회하거나 신규 생성(upsert)하여 로그인 결과를 반환한다."""
        pass
