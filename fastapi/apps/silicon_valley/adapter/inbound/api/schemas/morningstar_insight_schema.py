from pydantic import BaseModel, Field


class MorningstarInsightSchema(BaseModel):

    question: str = Field(..., description="금융 전문가의 질문")
    report_limit: int = Field(5, description="근거로 사용할 최신 보고서 개수")

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "최근 보고서에서 언급된 주요 리스크 요인은?",
                "report_limit": 5,
            }
        }
    }


class MorningstarInsightResultSchema(BaseModel):

    question: str = Field(..., description="입력된 질문")
    insight: str = Field(..., description="생성된 금융 인사이트")
    sources: list[str] = Field(..., description="근거로 사용된 보고서 파일명 목록")
