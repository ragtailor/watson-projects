from pydantic import BaseModel, Field


class SemanticChatSchema(BaseModel):

    session_id: str | None = Field(None, description="대화 세션 ID (없으면 새로 발급)")
    message: str = Field(..., description="사용자 메시지")

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": None,
                "message": "안녕하세요, 요금 문의드립니다.",
            }
        }
    }


class SemanticChatResultSchema(BaseModel):

    session_id: str = Field(..., description="대화 세션 ID")
    intent: str = Field(..., description="판단된 의도")
    reply: str = Field(..., description="챗봇 응답")
