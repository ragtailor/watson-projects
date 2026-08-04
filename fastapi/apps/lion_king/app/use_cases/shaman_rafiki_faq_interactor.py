from __future__ import annotations

from lion_king.adapter.inbound.api.schemas.shaman_rafiki_faq_schema import RafikiFaqSchema
from lion_king.app.dtos.shaman_rafiki_faq_dto import RafikiFaqQuery, RafikiFaqResponse
from lion_king.app.ports.input.shaman_rafiki_faq_use_case import RafikiFaqUseCase
from lion_king.app.ports.output.shaman_rafiki_faq_repository import RafikiFaqRepository


class RafikiFaqInteractor(RafikiFaqUseCase):

    def __init__(self, repository: RafikiFaqRepository):
        self.repository = repository

    async def introduce_myself(self, schema: RafikiFaqSchema) -> RafikiFaqResponse:
        '''라피키의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(RafikiFaqQuery(
            id = schema.id,
            name = schema.name
        ))
