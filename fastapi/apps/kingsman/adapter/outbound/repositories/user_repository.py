from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from kingsman.adapter.outbound.orm.user_orm import UserOrm
from kingsman.app.dtos.oauth_dto import OAuthLoginResult, OAuthProfile
from kingsman.app.ports.output.user_repository_port import UserRepositoryPort

logger = logging.getLogger(__name__)


class UserRepository(UserRepositoryPort):
    """UserRepositoryPort 구현 — kingsman_users 테이블."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_oauth(self, provider: str, subject: str) -> OAuthLoginResult | None:
        stmt = select(UserOrm).where(
            UserOrm.oauth_provider == provider, UserOrm.oauth_subject == subject
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return OAuthLoginResult(user_id=row.user_id, nickname=row.nickname, email=row.email)

    async def upsert_oauth_user(self, profile: OAuthProfile) -> OAuthLoginResult:
        user_id = f"{profile.provider}_{profile.subject}"
        row = UserOrm(
            user_id=user_id,
            nickname=profile.nickname,
            email=profile.email,
            oauth_provider=profile.provider,
            oauth_subject=profile.subject,
        )
        self.session.add(row)
        await self.session.commit()
        logger.info(
            "[UserRepository] OAuth 신규 사용자 생성 — provider=%s user_id=%s", profile.provider, user_id
        )
        return OAuthLoginResult(user_id=user_id, nickname=profile.nickname, email=profile.email)
