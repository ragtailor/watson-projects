from dataclasses import dataclass, field


@dataclass(frozen=True)
class ClassifyImageQuery:

    filename: str
    content_type: str
    size: int
    data: bytes
    top_k: int = 5


@dataclass(frozen=True)
class LabelScore:

    label: str
    confidence: float


@dataclass(frozen=True)
class ClassifyImageResponse:

    label: str
    confidence: float
    top5: list[LabelScore] = field(default_factory=list)
