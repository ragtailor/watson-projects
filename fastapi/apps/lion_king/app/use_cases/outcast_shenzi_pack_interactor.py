from __future__ import annotations

from lion_king.adapter.inbound.api.schemas.outcast_shenzi_pack_schema import ShenziPackSchema
from lion_king.app.dtos.outcast_shenzi_pack_dto import ShenziPackQuery, ShenziPackResponse
from lion_king.app.ports.input.outcast_shenzi_pack_use_case import ShenziPackUseCase
from lion_king.app.ports.output.outcast_shenzi_pack_repository import ShenziPackRepository


class ShenziPackInteractor(ShenziPackUseCase):

    def __init__(self, repository: ShenziPackRepository):
        self.repository = repository

    async def introduce_myself(self, schema: ShenziPackSchema) -> ShenziPackResponse:
        '''셴지의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(ShenziPackQuery(
            id = schema.id,
            name = schema.name
        ))
