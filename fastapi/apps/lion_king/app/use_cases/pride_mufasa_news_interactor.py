from __future__ import annotations

from lion_king.adapter.inbound.api.schemas.pride_mufasa_news_schema import MufasaNewsSchema
from lion_king.app.dtos.pride_mufasa_news_dto import MufasaNewsQuery, MufasaNewsResponse
from lion_king.app.ports.input.pride_mufasa_news_use_case import MufasaNewsUseCase
from lion_king.app.ports.output.pride_mufasa_news_repository import MufasaNewsRepository


class MufasaNewsInteractor(MufasaNewsUseCase):

    def __init__(self, repository: MufasaNewsRepository):
        self.repository = repository

    async def introduce_myself(self, schema: MufasaNewsSchema) -> MufasaNewsResponse:
        '''무파사의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(MufasaNewsQuery(
            id = schema.id,
            name = schema.name
        ))
