from fastapi import APIRouter, Depends, HTTPException

from silicon_valley.adapter.inbound.api.schemas.piper_monica_graph_schema import (
    MonicaAskResultSchema,
    MonicaAskSchema,
    MonicaIngestResultSchema,
)
from silicon_valley.app.dtos.piper_monica_graph_dto import MonicaAskQuery, MonicaIngestCommand
from silicon_valley.app.ports.input.knowledge_graph_ingest_use_case import KnowledgeGraphIngestUseCase
from silicon_valley.app.ports.input.piper_monica_graph_use_case import PiperMonicaGraphUseCase
from silicon_valley.dependencies.piper_monica_graph_provider import (
    get_knowledge_graph_ingest_use_case,
    get_piper_monica_graph_use_case,
)

'''
모니카 — Pgvector + Neo4j 하이브리드 검색 에이전트 (009 전략 5~9단계)
'''
monica_graph_router = APIRouter(prefix="/monica", tags=["monica"])


@monica_graph_router.post(
    "/ask",
    response_model=MonicaAskResultSchema,
    summary="하이브리드(벡터+그래프) 검색으로 질문에 답변",
)
async def ask(
    schema: MonicaAskSchema,
    use_case: PiperMonicaGraphUseCase = Depends(get_piper_monica_graph_use_case),
) -> MonicaAskResultSchema:

    response = await use_case.ask(MonicaAskQuery(question=schema.question, top_k=schema.top_k))

    return MonicaAskResultSchema(
        question=response.question,
        route=response.route,
        answer=response.answer,
        vector_hits=response.vector_hits,
        graph_hits=response.graph_hits,
        retry_count=response.retry_count,
    )


@monica_graph_router.post(
    "/ingest/{document_id}",
    response_model=MonicaIngestResultSchema,
    summary="적재된 문서에서 엔티티·관계를 추출해 지식 그래프에 적재",
)
async def ingest(
    document_id: int,
    use_case: KnowledgeGraphIngestUseCase = Depends(get_knowledge_graph_ingest_use_case),
) -> MonicaIngestResultSchema:

    try:
        response = await use_case.ingest(MonicaIngestCommand(document_id=document_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return MonicaIngestResultSchema(
        document_id=response.document_id,
        filename=response.filename,
        entity_count=response.entity_count,
        relation_count=response.relation_count,
    )
