from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.adapter.inbound.api.schemas.savanna_zazu_hornbill_schema import ZazuHornbillSchema
from lion_king.app.dtos.savanna_zazu_hornbill_dto import ZazuHornbillResponse


class ZazuHornbillUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: ZazuHornbillSchema) -> ZazuHornbillResponse:
        '''자주의 자기소개 메소드'''
        pass
