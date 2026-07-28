from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.domain.document_vector import DocumentVector


class MorningstarInsightGeneratorPort(ABC):

    @abstractmethod
    async def generate(self, question: str, reports: list[DocumentVector]) -> str:
        '''보고서 컨텍스트와 질문을 맞춤형 프롬프트로 결합해 금융 인사이트를 생성하는 추상 메소드'''
        pass
