from __future__ import annotations

from kingsman.app.dtos.oauth_dto import OAuthLoginResult, OAuthProfile
from kingsman.app.ports.input.oauth_login_use_case import OAuthLoginUseCase
from kingsman.app.ports.output.user_repository_port import UserRepositoryPort


class OAuthLoginInteractor(OAuthLoginUseCase):

    def __init__(self, users: UserRepositoryPort) -> None:
        self._users = users

    async def login_with_profile(self, profile: OAuthProfile) -> OAuthLoginResult:
        existing = await self._users.find_by_oauth(profile.provider, profile.subject)
        if existing is not None:
            return existing
        return await self._users.upsert_oauth_user(profile)
