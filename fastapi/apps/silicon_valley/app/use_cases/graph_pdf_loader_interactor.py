from __future__ import annotations

from silicon_valley.app.dtos.graph_pdf_loader_dto import GraphPdfLoaderCommand, GraphPdfLoaderResponse
from silicon_valley.app.ports.input.graph_pdf_loader_use_case import GraphPdfLoaderUseCase
from silicon_valley.app.ports.output.graph_document_summarizer_port import GraphDocumentSummarizerPort
from silicon_valley.app.ports.output.graph_document_vector_port import GraphDocumentVectorPort
from silicon_valley.app.ports.output.graph_pdf_extractor_port import GraphPdfExtractorPort
from silicon_valley.app.ports.output.knowledge_chunk_repository_port import KnowledgeChunkRepositoryPort
from silicon_valley.app.ports.output.knowledge_embedder_port import KnowledgeEmbedderPort
from silicon_valley.domain.knowledge_chunk import split_into_chunks


class GraphPdfLoaderInteractor(GraphPdfLoaderUseCase):

    def __init__(
        self,
        extractor: GraphPdfExtractorPort,
        summarizer: GraphDocumentSummarizerPort,
        repository: GraphDocumentVectorPort,
        embedder: KnowledgeEmbedderPort,
        chunk_repository: KnowledgeChunkRepositoryPort,
    ):
        self.extractor = extractor
        self.summarizer = summarizer
        self.repository = repository
        self.embedder = embedder
        self.chunk_repository = chunk_repository

    async def upload(self, command: GraphPdfLoaderCommand) -> GraphPdfLoaderResponse:
        '''PDF 업로드 파이프라인: 본문 추출 → 요약 → 저장 → 조각 임베딩 적재'''

        text = await self.extractor.extract_text(command.filename, command.file_bytes)
        summary = await self.summarizer.summarize(text)
        document = await self.repository.save(
            filename=command.filename,
            content=text,
            summary=summary,
        )

        chunk_count = await self._ingest_chunks(document.id, text)

        return GraphPdfLoaderResponse(
            id=document.id,
            filename=document.filename,
            summary=document.summary,
            chunk_count=chunk_count,
        )

    async def _ingest_chunks(self, document_id: int, text: str) -> int:
        '''본문을 조각으로 나눠 임베딩과 함께 적재한다. 벡터 검색의 대상이 되는 단위다.'''

        contents = split_into_chunks(text)
        if not contents:
            return 0

        embeddings = await self.embedder.embed_all(contents)

        return await self.chunk_repository.save_all(
            document_id=document_id,
            contents=contents,
            embeddings=embeddings,
        )
