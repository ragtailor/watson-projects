from __future__ import annotations

from lion_king.adapter.inbound.api.schemas.outcast_hyena_graveyard_schema import HyenaGraveyardSchema
from lion_king.app.dtos.outcast_hyena_graveyard_dto import HyenaGraveyardQuery, HyenaGraveyardResponse
from lion_king.app.ports.input.outcast_hyena_graveyard_use_case import HyenaGraveyardUseCase
from lion_king.app.ports.output.outcast_hyena_graveyard_repository import HyenaGraveyardRepository


class HyenaGraveyardInteractor(HyenaGraveyardUseCase):

    def __init__(self, repository: HyenaGraveyardRepository):
        self.repository = repository

    async def introduce_myself(self, schema: HyenaGraveyardSchema) -> HyenaGraveyardResponse:
        '''하이에나 무리의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(HyenaGraveyardQuery(
            id = schema.id,
            name = schema.name
        ))
