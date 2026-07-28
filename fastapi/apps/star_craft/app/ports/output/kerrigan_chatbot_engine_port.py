from __future__ import annotations

from abc import ABC, abstractmethod


class KerriganChatbotEnginePort(ABC):

    @abstractmethod
    async def reply(self, message: str, intent: str) -> str:
        '''판단된 의도를 참고해 LangChain 챗봇 엔진으로 응답을 생성하는 추상 메소드'''
        pass
