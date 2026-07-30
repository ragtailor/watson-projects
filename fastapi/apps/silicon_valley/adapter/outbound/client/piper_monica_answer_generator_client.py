from __future__ import annotations

import os

from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from silicon_valley.app.ports.output.piper_monica_answer_generator_port import (
    PiperMonicaAnswerGeneratorPort,
)

_OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "exaone3.5:2.4b")

_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "당신은 파이드 파이퍼의 지식 분석가 모니카입니다. 아래 근거만 사용해 한국어로 "
        "간결하게 답하세요. 근거에 없는 내용은 추측하지 마세요.\n"
        "근거 충분 여부: {evidence_state}\n"
        "근거가 부족하면 무엇이 부족한지 먼저 한 문장으로 밝히세요.\n\n"
        "[문서 조각]\n{vector_context}\n\n[관계망]\n{graph_context}",
    ),
    ("human", "{question}"),
])


class PiperMonicaAnswerGeneratorClient(PiperMonicaAnswerGeneratorPort):
    '''LangChain 체인(prompt | llm | parser)으로 하이브리드 근거를 묶어 답변을 만든다.'''

    def __init__(self) -> None:
        llm = ChatOllama(base_url=_OLLAMA_BASE_URL, model=_OLLAMA_MODEL)
        self._chain = _PROMPT | llm | StrOutputParser()

    async def generate(
        self,
        question: str,
        vector_hits: list[str],
        graph_hits: list[str],
        evidence_sufficient: bool,
    ) -> str:
        return await self._chain.ainvoke({
            "question": question,
            "vector_context": "\n---\n".join(vector_hits) or "(없음)",
            "graph_context": "\n".join(graph_hits) or "(없음)",
            "evidence_state": "충분" if evidence_sufficient else "부족",
        })
