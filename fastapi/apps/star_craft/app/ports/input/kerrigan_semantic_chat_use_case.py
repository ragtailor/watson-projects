from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.kerrigan_semantic_dto import KerriganChatCommand, KerriganChatResponse


class KerriganSemanticChatUseCase(ABC):

    @abstractmethod
    async def chat(self, command: KerriganChatCommand) -> KerriganChatResponse:
        '''메시지의 의도를 시멘틱으로 판단한 뒤 챗봇 엔진과 대화하는 메소드'''
        pass
