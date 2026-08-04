from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.adapter.inbound.api.schemas.savanna_pumba_warthog_schema import PumbaWarthogSchema
from lion_king.app.dtos.savanna_pumba_warthog_dto import PumbaWarthogResponse


class PumbaWarthogUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: PumbaWarthogSchema) -> PumbaWarthogResponse:
        '''품바의 자기소개 메소드'''
        pass
