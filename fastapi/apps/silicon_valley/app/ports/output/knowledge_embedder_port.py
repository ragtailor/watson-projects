from __future__ import annotations

from abc import ABC, abstractmethod


class KnowledgeEmbedderPort(ABC):

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        '''텍스트 한 조각을 임베딩 벡터로 변환하는 추상 메소드'''
        pass

    @abstractmethod
    async def embed_all(self, texts: list[str]) -> list[list[float]]:
        '''여러 조각을 한 번에 임베딩하는 추상 메소드'''
        pass
