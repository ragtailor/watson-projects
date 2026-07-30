from pydantic import BaseModel, Field


class GraphPdfLoaderResultSchema(BaseModel):

    id: int = Field(..., description="저장된 문서 ID")
    filename: str = Field(..., description="업로드된 PDF 파일명")
    summary: str = Field(..., description="추출된 본문의 요약")
    chunk_count: int = Field(..., description="벡터 검색용으로 적재된 조각 수")
