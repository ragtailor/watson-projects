from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.adapter.inbound.api.schemas.outcast_hyena_graveyard_schema import HyenaGraveyardSchema
from lion_king.app.dtos.outcast_hyena_graveyard_dto import HyenaGraveyardResponse


class HyenaGraveyardUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: HyenaGraveyardSchema) -> HyenaGraveyardResponse:
        '''하이에나 무리의 자기소개 메소드'''
        pass
