from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.adapter.inbound.api.schemas.pride_mufasa_news_schema import MufasaNewsSchema
from lion_king.app.dtos.pride_mufasa_news_dto import MufasaNewsResponse


class MufasaNewsUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: MufasaNewsSchema) -> MufasaNewsResponse:
        '''무파사의 자기소개 메소드'''
        pass
