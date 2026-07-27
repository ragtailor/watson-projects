from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from silicon_valley.adapter.outbound.client.graph_document_summarizer_client import GraphDocumentSummarizerClient
from silicon_valley.adapter.outbound.loader.graph_pdf_extractor import GraphPdfExtractor
from silicon_valley.adapter.outbound.repository.document_vector_repository import DocumentVectorRepository
from silicon_valley.app.ports.input.graph_pdf_loader_use_case import GraphPdfLoaderUseCase
from silicon_valley.app.ports.output.graph_document_summarizer_port import GraphDocumentSummarizerPort
from silicon_valley.app.ports.output.graph_document_vector_port import GraphDocumentVectorPort
from silicon_valley.app.ports.output.graph_pdf_extractor_port import GraphPdfExtractorPort
from silicon_valley.app.use_cases.graph_pdf_loader_interactor import GraphPdfLoaderInteractor


def get_graph_pdf_extractor() -> GraphPdfExtractorPort:
    return GraphPdfExtractor()


def get_graph_document_summarizer() -> GraphDocumentSummarizerPort:
    return GraphDocumentSummarizerClient()


def get_document_vector_repository(
    db: AsyncSession = Depends(get_db),
) -> GraphDocumentVectorPort:
    return DocumentVectorRepository(session=db)


def get_graph_pdf_loader_use_case(
    extractor: GraphPdfExtractorPort = Depends(get_graph_pdf_extractor),
    summarizer: GraphDocumentSummarizerPort = Depends(get_graph_document_summarizer),
    repository: GraphDocumentVectorPort = Depends(get_document_vector_repository),
) -> GraphPdfLoaderUseCase:

    return GraphPdfLoaderInteractor(
        extractor=extractor,
        summarizer=summarizer,
        repository=repository,
    )
