from __future__ import annotations

from abc import ABC, abstractmethod


class GraphDocumentSummarizerPort(ABC):

    @abstractmethod
    async def summarize(self, text: str) -> str:
        '''추출된 본문 텍스트를 요약하는 추상 메소드'''
        pass
