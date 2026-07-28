from __future__ import annotations

import asyncio

from star_craft.app.dtos.kerrigan_semantic_dto import KerriganChatCommand, KerriganChatResponse
from star_craft.app.ports.input.kerrigan_semantic_chat_use_case import KerriganSemanticChatUseCase
from star_craft.app.ports.output.kerrigan_chatbot_engine_port import KerriganChatbotEnginePort
from star_craft.app.ports.output.kerrigan_conversation_repository_port import (
    KerriganConversationRepositoryPort,
)
from star_craft.app.ports.output.kerrigan_intent_port import KerriganIntentPort


class KerriganSemanticChatInteractor(KerriganSemanticChatUseCase):

    def __init__(
        self,
        intent_classifier: KerriganIntentPort,
        chatbot_engine: KerriganChatbotEnginePort,
        conversation_repository: KerriganConversationRepositoryPort,
    ):
        self.intent_classifier = intent_classifier
        self.chatbot_engine = chatbot_engine
        self.conversation_repository = conversation_repository

    async def chat(self, command: KerriganChatCommand) -> KerriganChatResponse:
        '''시멘틱 의도 판단(스레드풀) → LangChain 챗봇 응답 → 대화 턴 저장'''

        # Kiwi 형태소 분석은 CPU-bound이므로 스레드풀로 넘겨 이벤트 루프를 막지 않는다.
        intent = await asyncio.to_thread(self.intent_classifier.analyze_intent, command.message)
        reply = await self.chatbot_engine.reply(command.message, intent)
        await self.conversation_repository.save_turn(
            session_id=command.session_id,
            message=command.message,
            intent=intent,
            reply=reply,
        )

        return KerriganChatResponse(session_id=command.session_id, intent=intent, reply=reply)
