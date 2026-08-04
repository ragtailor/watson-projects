from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.adapter.inbound.api.schemas.pride_nala_queen_schema import NalaQueenSchema
from lion_king.app.dtos.pride_nala_queen_dto import NalaQueenResponse


class NalaQueenUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: NalaQueenSchema) -> NalaQueenResponse:
        '''날라의 자기소개 메소드'''
        pass
