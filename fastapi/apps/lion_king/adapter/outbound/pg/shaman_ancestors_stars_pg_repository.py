from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession

from lion_king.app.dtos.shaman_ancestors_stars_dto import AncestorsStarsQuery, AncestorsStarsResponse
from lion_king.app.ports.output.shaman_ancestors_stars_repository import AncestorsStarsRepository


class AncestorsStarsPgRepository(AncestorsStarsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: AncestorsStarsQuery) -> AncestorsStarsResponse:

        '''선조들의 자기 소개 레포지토리 구현 메소드'''

        logger.info(f"[AncestorsStarsPgRepository] introduce_myself 진입 | request_data={query}")

        response: AncestorsStarsResponse = AncestorsStarsResponse(
            id= query.id * 10000,
            name= query.name + "가 레포지토리에 다녀옴"
        )
        return response
