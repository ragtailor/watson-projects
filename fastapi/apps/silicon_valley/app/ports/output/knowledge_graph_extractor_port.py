from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.domain.knowledge_graph_fact import KnowledgeGraphFacts


class KnowledgeGraphExtractorPort(ABC):

    @abstractmethod
    async def extract(self, text: str) -> KnowledgeGraphFacts:
        '''본문에서 엔티티와 관계를 추출하는 추상 메소드'''
        pass
