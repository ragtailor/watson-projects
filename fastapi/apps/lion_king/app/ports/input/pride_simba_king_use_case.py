from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.adapter.inbound.api.schemas.pride_simba_king_schema import SimbaKingSchema
from lion_king.app.dtos.pride_simba_king_dto import SimbaKingResponse


class SimbaKingUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: SimbaKingSchema) -> SimbaKingResponse:
        '''심바의 자기소개 메소드'''
        pass
