from pydantic import BaseModel, Field


class LabelScoreSchema(BaseModel):

    label: str = Field(..., description="ImageNet 라벨명")
    confidence: float = Field(..., description="신뢰도 (0~1)")


class ClassifyImageResponseSchema(BaseModel):

    label: str = Field(..., description="최상위 예측 라벨")
    confidence: float = Field(..., description="최상위 예측 신뢰도 (0~1)")
    top5: list[LabelScoreSchema] = Field(..., description="상위 top-k 예측 목록")
