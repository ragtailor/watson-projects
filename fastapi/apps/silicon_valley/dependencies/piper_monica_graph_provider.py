from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_architect_graph_manager import get_driver
from core.matrix.grid_oracle_database_manager import get_db

from silicon_valley.adapter.outbound.client.graph_reasoning_client import GraphReasoningClient
from silicon_valley.adapter.outbound.client.knowledge_graph_extractor_client import (
    KnowledgeGraphExtractorClient,
)
from silicon_valley.adapter.outbound.client.piper_monica_answer_generator_client import (
    PiperMonicaAnswerGeneratorClient,
)
from silicon_valley.adapter.outbound.repository.document_vector_repository import DocumentVectorRepository
from silicon_valley.adapter.outbound.repository.knowledge_graph_repository import KnowledgeGraphRepository
from silicon_valley.app.ports.input.knowledge_graph_ingest_use_case import KnowledgeGraphIngestUseCase
from silicon_valley.app.ports.input.piper_monica_graph_use_case import PiperMonicaGraphUseCase
from silicon_valley.app.ports.output.document_reader_port import DocumentReaderPort
from silicon_valley.app.ports.output.graph_reasoning_port import GraphReasoningPort
from silicon_valley.app.ports.output.knowledge_chunk_repository_port import KnowledgeChunkRepositoryPort
from silicon_valley.app.ports.output.knowledge_embedder_port import KnowledgeEmbedderPort
from silicon_valley.app.ports.output.knowledge_graph_extractor_port import KnowledgeGraphExtractorPort
from silicon_valley.app.ports.output.knowledge_graph_repository_port import KnowledgeGraphRepositoryPort
from silicon_valley.app.ports.output.piper_monica_answer_generator_port import (
    PiperMonicaAnswerGeneratorPort,
)
from silicon_valley.app.use_cases.knowledge_graph_ingest_interactor import KnowledgeGraphIngestInteractor
from silicon_valley.app.use_cases.langgraph_interactor import LangGraphReasoningInteractor
from silicon_valley.dependencies.graph_pdf_loader_provider import (
    get_knowledge_chunk_repository,
    get_knowledge_embedder,
)


def get_document_reader(db: AsyncSession = Depends(get_db)) -> DocumentReaderPort:
    return DocumentVectorRepository(session=db)


def get_knowledge_graph_extractor() -> KnowledgeGraphExtractorPort:
    return KnowledgeGraphExtractorClient()


def get_knowledge_graph_repository() -> KnowledgeGraphRepositoryPort:
    return KnowledgeGraphRepository(driver=get_driver())


def get_graph_reasoning() -> GraphReasoningPort:
    return GraphReasoningClient(driver=get_driver())


def get_monica_answer_generator() -> PiperMonicaAnswerGeneratorPort:
    return PiperMonicaAnswerGeneratorClient()


def get_knowledge_graph_ingest_use_case(
    document_reader: DocumentReaderPort = Depends(get_document_reader),
    extractor: KnowledgeGraphExtractorPort = Depends(get_knowledge_graph_extractor),
    graph_repository: KnowledgeGraphRepositoryPort = Depends(get_knowledge_graph_repository),
) -> KnowledgeGraphIngestUseCase:

    return KnowledgeGraphIngestInteractor(
        document_reader=document_reader,
        extractor=extractor,
        graph_repository=graph_repository,
    )


def get_piper_monica_graph_use_case(
    embedder: KnowledgeEmbedderPort = Depends(get_knowledge_embedder),
    chunk_repository: KnowledgeChunkRepositoryPort = Depends(get_knowledge_chunk_repository),
    graph_reasoning: GraphReasoningPort = Depends(get_graph_reasoning),
    answer_generator: PiperMonicaAnswerGeneratorPort = Depends(get_monica_answer_generator),
) -> PiperMonicaGraphUseCase:

    return LangGraphReasoningInteractor(
        embedder=embedder,
        chunk_repository=chunk_repository,
        graph_reasoning=graph_reasoning,
        answer_generator=answer_generator,
    )
