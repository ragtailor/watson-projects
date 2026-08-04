from __future__ import annotations

from lion_king.adapter.inbound.api.schemas.outcast_scar_chatbot_schema import ScarChatbotSchema
from lion_king.app.dtos.outcast_scar_chatbot_dto import ScarChatbotQuery, ScarChatbotResponse
from lion_king.app.ports.input.outcast_scar_chatbot_use_case import ScarChatbotUseCase
from lion_king.app.ports.output.outcast_scar_chatbot_repository import ScarChatbotRepository


class ScarChatbotInteractor(ScarChatbotUseCase):

    def __init__(self, repository: ScarChatbotRepository):
        self.repository = repository

    async def introduce_myself(self, schema: ScarChatbotSchema) -> ScarChatbotResponse:
        '''스카의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(ScarChatbotQuery(
            id = schema.id,
            name = schema.name
        ))
