from __future__ import annotations

from lion_king.adapter.inbound.api.schemas.savanna_pumba_warthog_schema import PumbaWarthogSchema
from lion_king.app.dtos.savanna_pumba_warthog_dto import PumbaWarthogQuery, PumbaWarthogResponse
from lion_king.app.ports.input.savanna_pumba_warthog_use_case import PumbaWarthogUseCase
from lion_king.app.ports.output.savanna_pumba_warthog_repository import PumbaWarthogRepository


class PumbaWarthogInteractor(PumbaWarthogUseCase):

    def __init__(self, repository: PumbaWarthogRepository):
        self.repository = repository

    async def introduce_myself(self, schema: PumbaWarthogSchema) -> PumbaWarthogResponse:
        '''품바의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(PumbaWarthogQuery(
            id = schema.id,
            name = schema.name
        ))
