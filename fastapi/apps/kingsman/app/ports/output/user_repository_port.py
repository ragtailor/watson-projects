from __future__ import annotations

from abc import ABC, abstractmethod

from kingsman.app.dtos.oauth_dto import OAuthLoginResult, OAuthProfile


class UserRepositoryPort(ABC):

    @abstractmethod
    async def find_by_oauth(self, provider: str, subject: str) -> OAuthLoginResult | None:
        """(provider, subject) 조합으로 기존 사용자를 조회한다. 없으면 None."""
        pass

    @abstractmethod
    async def upsert_oauth_user(self, profile: OAuthProfile) -> OAuthLoginResult:
        """OAuth 프로필로 사용자를 신규 생성하거나 갱신한다."""
        pass
