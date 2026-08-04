from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from lion_king.app.dtos.outcast_hyena_graveyard_dto import HyenaGraveyardQuery, HyenaGraveyardResponse
from lion_king.app.ports.output.outcast_hyena_graveyard_repository import HyenaGraveyardRepository


class HyenaGraveyardPgRepository(HyenaGraveyardRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: HyenaGraveyardQuery) -> HyenaGraveyardResponse:

        '''하이에나 무리의 자기 소개 레포지토리 구현 메소드'''

        logger.info(f"[HyenaGraveyardPgRepository] introduce_myself 진입 | request_data={query}")

        response: HyenaGraveyardResponse = HyenaGraveyardResponse(
            id= query.id * 10000,
            name= query.name + "가 레포지토리에 다녀옴"
        )
        return response
