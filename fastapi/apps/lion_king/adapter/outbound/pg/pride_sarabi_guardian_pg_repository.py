from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from lion_king.app.dtos.pride_sarabi_guardian_dto import SarabiGuardianQuery, SarabiGuardianResponse
from lion_king.app.ports.output.pride_sarabi_guardian_repository import SarabiGuardianRepository


class SarabiGuardianPgRepository(SarabiGuardianRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: SarabiGuardianQuery) -> SarabiGuardianResponse:

        '''사라비의 자기 소개 레포지토리 구현 메소드'''

        logger.info(f"[SarabiGuardianPgRepository] introduce_myself 진입 | request_data={query}")

        response: SarabiGuardianResponse = SarabiGuardianResponse(
            id= query.id * 10000,
            name= query.name + "가 레포지토리에 다녀옴"
        )
        return response
