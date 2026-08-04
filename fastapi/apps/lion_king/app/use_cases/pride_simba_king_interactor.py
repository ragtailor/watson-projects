from __future__ import annotations

from lion_king.adapter.inbound.api.schemas.pride_simba_king_schema import SimbaKingSchema
from lion_king.app.dtos.pride_simba_king_dto import SimbaKingQuery, SimbaKingResponse
from lion_king.app.ports.input.pride_simba_king_use_case import SimbaKingUseCase
from lion_king.app.ports.output.pride_simba_king_repository import SimbaKingRepository


class SimbaKingInteractor(SimbaKingUseCase):

    def __init__(self, repository: SimbaKingRepository):
        self.repository = repository

    async def introduce_myself(self, schema: SimbaKingSchema) -> SimbaKingResponse:
        '''심바의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(SimbaKingQuery(
            id = schema.id,
            name = schema.name
        ))
