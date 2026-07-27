from __future__ import annotations

from silicon_valley.app.dtos.graph_pdf_loader_dto import GraphPdfLoaderCommand, GraphPdfLoaderResponse
from silicon_valley.app.ports.input.graph_pdf_loader_use_case import GraphPdfLoaderUseCase
from silicon_valley.app.ports.output.graph_document_summarizer_port import GraphDocumentSummarizerPort
from silicon_valley.app.ports.output.graph_document_vector_port import GraphDocumentVectorPort
from silicon_valley.app.ports.output.graph_pdf_extractor_port import GraphPdfExtractorPort


class GraphPdfLoaderInteractor(GraphPdfLoaderUseCase):

    def __init__(
        self,
        extractor: GraphPdfExtractorPort,
        summarizer: GraphDocumentSummarizerPort,
        repository: GraphDocumentVectorPort,
    ):
        self.extractor = extractor
        self.summarizer = summarizer
        self.repository = repository

    async def upload(self, command: GraphPdfLoaderCommand) -> GraphPdfLoaderResponse:
        '''PDF 업로드 파이프라인: 본문 추출 → 요약 → 저장'''

        text = await self.extractor.extract_text(command.filename, command.file_bytes)
        summary = await self.summarizer.summarize(text)
        document = await self.repository.save(
            filename=command.filename,
            content=text,
            summary=summary,
        )

        return GraphPdfLoaderResponse(
            id=document.id,
            filename=document.filename,
            summary=document.summary,
        )
