from __future__ import annotations

import os

from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from star_craft.app.ports.output.kerrigan_chatbot_engine_port import KerriganChatbotEnginePort

_OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "exaone3.5:2.4b")

_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "당신은 RAG Tailor 사이트의 챗봇 케리건(Kerrigan)입니다. "
        "사용자 메시지의 의도는 '{intent}'로 판단되었습니다. 이 의도를 참고해 "
        "친절하고 간결한 한국어로 답변하세요.",
    ),
    ("human", "{message}"),
])


class KerriganChatbotEngineClient(KerriganChatbotEnginePort):
    '''LangChain 체인(prompt | llm | parser)으로 의도를 반영한 응답을 생성한다.'''

    def __init__(self) -> None:
        llm = ChatOllama(base_url=_OLLAMA_BASE_URL, model=_OLLAMA_MODEL)
        self._chain = _PROMPT | llm | StrOutputParser()

    async def reply(self, message: str, intent: str) -> str:
        return await self._chain.ainvoke({"message": message, "intent": intent})
