from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from lion_king.app.dtos.savanna_zazu_hornbill_dto import ZazuHornbillQuery, ZazuHornbillResponse
from lion_king.app.ports.output.savanna_zazu_hornbill_repository import ZazuHornbillRepository


class ZazuHornbillPgRepository(ZazuHornbillRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: ZazuHornbillQuery) -> ZazuHornbillResponse:

        '''자주의 자기 소개 레포지토리 구현 메소드'''

        logger.info(f"[ZazuHornbillPgRepository] introduce_myself 진입 | request_data={query}")

        response: ZazuHornbillResponse = ZazuHornbillResponse(
            id= query.id * 10000,
            name= query.name + "가 레포지토리에 다녀옴"
        )
        return response
