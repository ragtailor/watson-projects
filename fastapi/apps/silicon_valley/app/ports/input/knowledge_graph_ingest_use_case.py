from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_monica_graph_dto import MonicaIngestCommand, MonicaIngestResponse


class KnowledgeGraphIngestUseCase(ABC):

    @abstractmethod
    async def ingest(self, command: MonicaIngestCommand) -> MonicaIngestResponse:
        '''적재된 문서에서 엔티티·관계를 추출해 Neo4j에 넣는 추상 메소드'''
        pass
