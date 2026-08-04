from __future__ import annotations

from lion_king.adapter.inbound.api.schemas.pride_nala_queen_schema import NalaQueenSchema
from lion_king.app.dtos.pride_nala_queen_dto import NalaQueenQuery, NalaQueenResponse
from lion_king.app.ports.input.pride_nala_queen_use_case import NalaQueenUseCase
from lion_king.app.ports.output.pride_nala_queen_repository import NalaQueenRepository


class NalaQueenInteractor(NalaQueenUseCase):

    def __init__(self, repository: NalaQueenRepository):
        self.repository = repository

    async def introduce_myself(self, schema: NalaQueenSchema) -> NalaQueenResponse:
        '''날라의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(NalaQueenQuery(
            id = schema.id,
            name = schema.name
        ))
