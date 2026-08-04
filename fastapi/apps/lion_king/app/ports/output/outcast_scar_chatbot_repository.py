from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.app.dtos.outcast_scar_chatbot_dto import ScarChatbotQuery, ScarChatbotResponse


class ScarChatbotRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: ScarChatbotQuery) -> ScarChatbotResponse:
        '''스카의 자기 소개 레포지토리 추상 메소드'''
        pass
