from dataclasses import dataclass, field


@dataclass(frozen=True)
class MonicaAskQuery:

    question: str
    top_k: int = 4


@dataclass(frozen=True)
class MonicaAskResponse:

    question: str
    route: str
    answer: str
    vector_hits: list[str] = field(default_factory=list)
    graph_hits: list[str] = field(default_factory=list)
    retry_count: int = 0


@dataclass(frozen=True)
class MonicaIngestCommand:

    document_id: int


@dataclass(frozen=True)
class MonicaIngestResponse:

    document_id: int
    filename: str
    entity_count: int
    relation_count: int
