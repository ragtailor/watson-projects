from __future__ import annotations

from abc import ABC, abstractmethod


class PiperMonicaAnswerGeneratorPort(ABC):

    @abstractmethod
    async def generate(
        self,
        question: str,
        vector_hits: list[str],
        graph_hits: list[str],
        evidence_sufficient: bool,
    ) -> str:
        '''검색된 근거를 묶어 최종 답변을 생성하는 추상 메소드

        evidence_sufficient가 False면 근거 부족을 답변에 명시하도록 프롬프트가 지시한다.
        '''
        pass
