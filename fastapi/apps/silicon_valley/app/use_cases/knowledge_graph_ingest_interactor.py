from __future__ import annotations

from silicon_valley.app.dtos.piper_monica_graph_dto import MonicaIngestCommand, MonicaIngestResponse
from silicon_valley.app.ports.input.knowledge_graph_ingest_use_case import KnowledgeGraphIngestUseCase
from silicon_valley.app.ports.output.knowledge_graph_extractor_port import KnowledgeGraphExtractorPort
from silicon_valley.app.ports.output.knowledge_graph_repository_port import KnowledgeGraphRepositoryPort
from silicon_valley.app.ports.output.document_reader_port import DocumentReaderPort


class KnowledgeGraphIngestInteractor(KnowledgeGraphIngestUseCase):
    '''문서 → 엔티티/관계 추출 → Neo4j 적재.

    업로드 요청 안에서 동기로 돌리지 않는 이유는 문서당 LLM 호출이 발생해 응답이
    길어지기 때문이다 (009 문서 2.2). 관리자가 문서 단위로 수동 트리거한다.
    '''

    def __init__(
        self,
        document_reader: DocumentReaderPort,
        extractor: KnowledgeGraphExtractorPort,
        graph_repository: KnowledgeGraphRepositoryPort,
    ) -> None:
        self.document_reader = document_reader
        self.extractor = extractor
        self.graph_repository = graph_repository

    async def ingest(self, command: MonicaIngestCommand) -> MonicaIngestResponse:
        document = await self.document_reader.find_by_id(command.document_id)
        if document is None:
            raise ValueError(f"문서를 찾을 수 없습니다: id={command.document_id}")

        facts = await self.extractor.extract(document.content)
        await self.graph_repository.ingest(
            document_id=command.document_id,
            filename=document.filename,
            facts=facts,
        )

        return MonicaIngestResponse(
            document_id=command.document_id,
            filename=document.filename,
            entity_count=len(facts.entities),
            relation_count=len(facts.relations),
        )
