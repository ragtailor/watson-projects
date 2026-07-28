from __future__ import annotations

import os

from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from silicon_valley.app.ports.output.morningstar_insight_generator_port import MorningstarInsightGeneratorPort
from silicon_valley.domain.document_vector import DocumentVector

_OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "exaone3.5:2.4b")

_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "당신은 모닝스타(Morningstar)의 금융 인텔리전스 엔진입니다. "
        "아래 최신 재무 보고서·시장 데이터를 근거로, 금융 전문가의 질문에 정확하고 "
        "개인화된 인사이트를 한국어로 제공하세요. 근거가 부족하면 그 한계를 명시하세요.\n\n"
        "[최신 재무 보고서]\n{context}",
    ),
    ("human", "{question}"),
])


class MorningstarInsightGeneratorClient(MorningstarInsightGeneratorPort):
    '''LangChain 체인(prompt | llm | parser)으로 실시간 보고서 컨텍스트와 질문을 결합해 인사이트를 생성한다.'''

    def __init__(self) -> None:
        llm = ChatOllama(base_url=_OLLAMA_BASE_URL, model=_OLLAMA_MODEL)
        self._chain = _PROMPT | llm | StrOutputParser()

    async def generate(self, question: str, reports: list[DocumentVector]) -> str:
        context = "\n\n".join(
            f"- {report.filename}: {report.summary}" for report in reports
        ) or "저장된 보고서가 없습니다."

        return await self._chain.ainvoke({"context": context, "question": question})
