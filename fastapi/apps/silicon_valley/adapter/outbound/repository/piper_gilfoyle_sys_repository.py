from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from silicon_valley.app.dtos.piper_gilfoyle_sys_dto import GilfoyleSysQuery, GilfoyleSysResponse
from silicon_valley.app.ports.output.piper_gilfoyle_sys_port import GilfoyleSysPort

logger = logging.getLogger(__name__)


class GilfoyleSysRepository(GilfoyleSysPort):
    """GilfoyleSysPort 구현 — 아직 DB를 조회하지 않는 자기소개 스텁이다.

    lion_king의 같은 계열 레포지터리(pride_simba_king_pg_repository)와 동일한 형태다.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: GilfoyleSysQuery) -> GilfoyleSysResponse:
        logger.info("[GilfoyleSysRepository] introduce_myself 진입 | query=%s", query)

        return GilfoyleSysResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴",
        )
