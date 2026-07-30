from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db

from silicon_valley.app.ports.input.piper_monica_graph_use_case import PiperMonicaGraphUseCase
from silicon_valley.dependencies.piper_monica_graph_provider import get_piper_monica_graph_use_case

from star_craft.adapter.outbound.client.kerrigan_chatbot_engine_client import KerriganChatbotEngineClient
from star_craft.adapter.outbound.client.kerrigan_engine_router_client import KerriganEngineRouterClient
from star_craft.adapter.outbound.repositories.kerrigan_conversation_repository import (
    KerriganConversationRepository,
)
from star_craft.adapter.outbound.repositories.kerrigan_intent_repository import KerriganIntentRepository
from star_craft.app.ports.input.kerrigan_semantic_chat_use_case import KerriganSemanticChatUseCase
from star_craft.app.ports.output.kerrigan_chatbot_engine_port import KerriganChatbotEnginePort
from star_craft.app.ports.output.kerrigan_conversation_repository_port import (
    KerriganConversationRepositoryPort,
)
from star_craft.app.ports.output.kerrigan_intent_port import KerriganIntentPort
from star_craft.app.use_cases.kerrigan_semantic_chat_interactor import KerriganSemanticChatInteractor


def get_kerrigan_intent_repository() -> KerriganIntentPort:
    return KerriganIntentRepository()


def get_kerrigan_chatbot_engine(
    reasoning_use_case: PiperMonicaGraphUseCase = Depends(get_piper_monica_graph_use_case),
) -> KerriganChatbotEnginePort:
    '''intent별 분기를 어댑터 계층에 둔다 — 인터랙터는 이 구성을 알지 못한다.'''
    return KerriganEngineRouterClient(
        linear_engine=KerriganChatbotEngineClient(),
        reasoning_use_case=reasoning_use_case,
    )


def get_kerrigan_conversation_repository(
    db: AsyncSession = Depends(get_db),
) -> KerriganConversationRepositoryPort:
    return KerriganConversationRepository(session=db)


def get_kerrigan_semantic_chat_use_case(
    intent_classifier: KerriganIntentPort = Depends(get_kerrigan_intent_repository),
    chatbot_engine: KerriganChatbotEnginePort = Depends(get_kerrigan_chatbot_engine),
    conversation_repository: KerriganConversationRepositoryPort = Depends(
        get_kerrigan_conversation_repository
    ),
) -> KerriganSemanticChatUseCase:

    return KerriganSemanticChatInteractor(
        intent_classifier=intent_classifier,
        chatbot_engine=chatbot_engine,
        conversation_repository=conversation_repository,
    )
