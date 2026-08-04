from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.adapter.inbound.api.schemas.outcast_shenzi_pack_schema import ShenziPackSchema
from lion_king.app.dtos.outcast_shenzi_pack_dto import ShenziPackResponse


class ShenziPackUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: ShenziPackSchema) -> ShenziPackResponse:
        '''셴지의 자기소개 메소드'''
        pass
