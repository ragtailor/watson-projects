from pydantic import BaseModel, Field


class MonicaAskSchema(BaseModel):

    question: str = Field(..., min_length=1, description="문서·관계망을 근거로 답할 질문")
    top_k: int = Field(4, ge=1, le=20, description="검색할 근거 개수")


class MonicaAskResultSchema(BaseModel):

    question: str = Field(..., description="입력 질문")
    route: str = Field(..., description="의도 분석 결과 (VECTOR / GRAPH)")
    answer: str = Field(..., description="생성된 답변")
    vector_hits: list[str] = Field(..., description="Pgvector 유사도 검색으로 찾은 문서 조각")
    graph_hits: list[str] = Field(..., description="Neo4j에서 찾은 관계망")
    retry_count: int = Field(..., description="보강 검색 횟수 (상한 도달 시 근거 부족 상태로 답변)")


class MonicaIngestResultSchema(BaseModel):

    document_id: int = Field(..., description="대상 문서 ID")
    filename: str = Field(..., description="문서 파일명")
    entity_count: int = Field(..., description="적재된 엔티티 수")
    relation_count: int = Field(..., description="적재된 관계 수")
