from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.adapter.inbound.api.schemas.shaman_rafiki_faq_schema import RafikiFaqSchema
from lion_king.app.dtos.shaman_rafiki_faq_dto import RafikiFaqResponse


class RafikiFaqUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: RafikiFaqSchema) -> RafikiFaqResponse:
        '''라피키의 자기소개 메소드'''
        pass
