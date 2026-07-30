from __future__ import annotations

import logging

from silicon_valley.app.dtos.piper_monica_graph_dto import MonicaAskQuery
from silicon_valley.app.ports.input.piper_monica_graph_use_case import PiperMonicaGraphUseCase

from star_craft.app.ports.output.kerrigan_chatbot_engine_port import KerriganChatbotEnginePort

logger = logging.getLogger(__name__)

# 004 하네스 규칙 1 — 기존 인텐트는 선형 체인이 그대로 처리한다.
# LangGraph는 실제로 조건 분기·보강 루프가 필요한 REASONING에만 연결한다.
REASONING_INTENT = "REASONING"


class KerriganEngineRouterClient(KerriganChatbotEnginePort):
    '''intent에 따라 선형 LangChain 체인과 LangGraph 에이전트로 분기하는 Strategy 어댑터.

    004 하네스 규칙 2 — KerriganSemanticChatInteractor는 이 분기를 알지 못한다.
    포트 시그니처(reply)가 그대로이므로 인터랙터를 수정하지 않았다.

    hub(star_craft)가 spoke(silicon_valley)를 임포트하는 것은 오케스트레이션 목적으로
    허용된다 (spoke → spoke 금지 규칙의 대상이 아니다).
    '''

    def __init__(
        self,
        linear_engine: KerriganChatbotEnginePort,
        reasoning_use_case: PiperMonicaGraphUseCase,
    ) -> None:
        self.linear_engine = linear_engine
        self.reasoning_use_case = reasoning_use_case

    async def reply(self, message: str, intent: str) -> str:
        if intent != REASONING_INTENT:
            return await self.linear_engine.reply(message, intent)

        try:
            response = await self.reasoning_use_case.ask(MonicaAskQuery(question=message))
            return response.answer
        except Exception as exc:
            # 추론 경로(Neo4j·pgvector·임베딩)가 하나라도 죽으면 챗봇 전체가 멈추므로
            # 선형 체인으로 내려앉는다. 기존 4개 인텐트의 동작에는 영향이 없다.
            logger.warning(
                f"[KerriganEngineRouterClient] LangGraph 위임 실패, 선형 체인으로 대체 | {exc}"
            )
            return await self.linear_engine.reply(message, intent)
