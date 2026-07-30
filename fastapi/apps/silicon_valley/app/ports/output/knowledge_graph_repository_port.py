from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.domain.knowledge_graph_fact import KnowledgeGraphFacts


class KnowledgeGraphRepositoryPort(ABC):

    @abstractmethod
    async def ingest(self, document_id: int, filename: str, facts: KnowledgeGraphFacts) -> int:
        '''추출된 엔티티·관계를 Neo4j에 적재하고 노드 수를 반환하는 추상 메소드'''
        pass
