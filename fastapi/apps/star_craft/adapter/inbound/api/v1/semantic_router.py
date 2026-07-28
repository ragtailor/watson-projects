from uuid import uuid4

from fastapi import APIRouter, Depends

from star_craft.adapter.inbound.api.schemas.semantic_schema import (
    SemanticChatResultSchema,
    SemanticChatSchema,
)
from star_craft.app.dtos.kerrigan_semantic_dto import KerriganChatCommand
from star_craft.app.ports.input.kerrigan_semantic_chat_use_case import KerriganSemanticChatUseCase
from star_craft.dependencies.kerrigan_semantic_chat_provider import get_kerrigan_semantic_chat_use_case

'''
사라 케리건 (Sarah Kerrigan)
star_craft 허브의 컨텍스트 라우터. 시멘틱(형태소 분석 기반)으로 메시지 의도를 판단한 뒤,
LangChain 챗봇 엔진과 대화를 이어간다.
'''
semantic_router = APIRouter(prefix="/semantic", tags=["semantic"])


@semantic_router.post(
    "/chat",
    response_model=SemanticChatResultSchema,
    summary="시멘틱 의도 판단 후 LangChain 챗봇과 대화",
)
async def chat(
    schema: SemanticChatSchema,
    use_case: KerriganSemanticChatUseCase = Depends(get_kerrigan_semantic_chat_use_case),
) -> SemanticChatResultSchema:

    session_id = schema.session_id or str(uuid4())
    response = await use_case.chat(
        KerriganChatCommand(session_id=session_id, message=schema.message)
    )

    return SemanticChatResultSchema(
        session_id=response.session_id,
        intent=response.intent,
        reply=response.reply,
    )
