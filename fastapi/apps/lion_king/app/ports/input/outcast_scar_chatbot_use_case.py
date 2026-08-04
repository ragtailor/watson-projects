from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.adapter.inbound.api.schemas.outcast_scar_chatbot_schema import ScarChatbotSchema
from lion_king.app.dtos.outcast_scar_chatbot_dto import ScarChatbotResponse


class ScarChatbotUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: ScarChatbotSchema) -> ScarChatbotResponse:
        '''스카의 자기소개 메소드'''
        pass
