from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.domain.knowledge_chunk import KnowledgeChunk


class KnowledgeChunkRepositoryPort(ABC):

    @abstractmethod
    async def save_all(
        self,
        document_id: int,
        contents: list[str],
        embeddings: list[list[float]],
    ) -> int:
        '''조각과 임베딩을 함께 저장하고 저장된 개수를 반환하는 추상 메소드'''
        pass

    @abstractmethod
    async def search_similar(self, embedding: list[float], limit: int) -> list[KnowledgeChunk]:
        '''질의 임베딩과 코사인 거리가 가까운 조각을 반환하는 추상 메소드'''
        pass
