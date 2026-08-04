from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from lion_king.app.dtos.outcast_shenzi_pack_dto import ShenziPackQuery, ShenziPackResponse
from lion_king.app.ports.output.outcast_shenzi_pack_repository import ShenziPackRepository


class ShenziPackPgRepository(ShenziPackRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: ShenziPackQuery) -> ShenziPackResponse:

        '''셴지의 자기 소개 레포지토리 구현 메소드'''

        logger.info(f"[ShenziPackPgRepository] introduce_myself 진입 | request_data={query}")

        response: ShenziPackResponse = ShenziPackResponse(
            id= query.id * 10000,
            name= query.name + "가 레포지토리에 다녀옴"
        )
        return response
