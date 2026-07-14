from pydantic import BaseModel, Field

class GilfoyleLlmSchema(BaseModel):

    prompt: str = Field(..., description="LLM에 전달할 프롬프트")
    max_new_tokens: int = Field(200, description="생성할 최대 토큰 수")
    temperature: float = Field(0.7, description="샘플링 온도")

    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "안녕하세요, 자기소개 해주세요.",
                "max_new_tokens": 200,
                "temperature": 0.7,
            }
        }
    }
