from __future__ import annotations

from abc import ABC, abstractmethod


class KerriganConversationRepositoryPort(ABC):

    @abstractmethod
    async def save_turn(self, session_id: str, message: str, intent: str, reply: str) -> None:
        '''대화 한 턴(질문·의도·응답)을 영속화하는 추상 메소드'''
        pass
