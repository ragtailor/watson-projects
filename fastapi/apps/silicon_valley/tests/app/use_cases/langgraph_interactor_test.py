from silicon_valley.app.use_cases.langgraph_interactor import (
    GENERATE_NODE,
    GRAPH_NODE,
    MAX_RETRY,
    VECTOR_NODE,
    LangGraphReasoningInteractor,
    decide_after_search,
    has_sufficient_evidence,
    route_entry,
)
from silicon_valley.domain.knowledge_chunk import KnowledgeChunk
from silicon_valley.domain.reasoning_route import GRAPH_ROUTE, VECTOR_ROUTE

_DIM = 768


class _FakeEmbedder:
    async def embed(self, text: str) -> list[float]:
        return [0.1] * _DIM

    async def embed_all(self, texts):
        return [await self.embed(t) for t in texts]


class _FakeChunkRepository:
    def __init__(self, hits: list[str]) -> None:
        self.hits = hits
        self.calls = 0

    async def save_all(self, document_id, contents, embeddings) -> int:
        return 0

    async def search_similar(self, embedding, limit) -> list[KnowledgeChunk]:
        self.calls += 1
        return [
            KnowledgeChunk(id=i, document_id=1, chunk_index=i, content=c)
            for i, c in enumerate(self.hits[:limit])
        ]


class _FakeGraphReasoning:
    def __init__(self, hits: list[str]) -> None:
        self.hits = hits
        self.calls = 0

    async def find_related(self, keywords, limit) -> list[str]:
        self.calls += 1
        return self.hits[:limit]


class _FakeAnswerGenerator:
    def __init__(self) -> None:
        self.last_sufficient: bool | None = None

    async def generate(self, question, vector_hits, graph_hits, evidence_sufficient) -> str:
        self.last_sufficient = evidence_sufficient
        return f"답변(조각 {len(vector_hits)}개, 관계 {len(graph_hits)}개)"


def _make(vector_hits=None, graph_hits=None):
    chunk_repository = _FakeChunkRepository(vector_hits or [])
    graph_reasoning = _FakeGraphReasoning(graph_hits or [])
    generator = _FakeAnswerGenerator()
    interactor = LangGraphReasoningInteractor(
        embedder=_FakeEmbedder(),
        chunk_repository=chunk_repository,
        graph_reasoning=graph_reasoning,
        answer_generator=generator,
    )
    return interactor, chunk_repository, graph_reasoning, generator


# ---- 노드 함수 ----

async def test_의도_분석_노드는_라우트와_재시도_횟수를_초기화한다():
    interactor, *_ = _make()

    state = await interactor.analyze_intent_node({"question": "두 인물의 관계를 알려줘"})

    assert state["route"] == GRAPH_ROUTE
    assert state["retry_count"] == 0


async def test_벡터_검색_노드는_조각_본문과_재시도_증가를_돌려준다():
    interactor, chunk_repository, _, _ = _make(vector_hits=["조각A", "조각B"])

    state = await interactor.vector_search_node({"question": "요약해줘", "top_k": 2, "retry_count": 0})

    assert state["vector_hits"] == ["조각A", "조각B"]
    assert state["retry_count"] == 1
    assert chunk_repository.calls == 1


async def test_그래프_검색_노드는_관계망과_재시도_증가를_돌려준다():
    interactor, _, graph_reasoning, _ = _make(graph_hits=["A -[X]-> B"])

    state = await interactor.graph_search_node({"question": "관계를 알려줘", "retry_count": 0})

    assert state["graph_hits"] == ["A -[X]-> B"]
    assert state["retry_count"] == 1
    assert graph_reasoning.calls == 1


async def test_생성_노드는_근거_충분_여부를_생성기에_전달한다():
    interactor, _, _, generator = _make()

    await interactor.generate_answer_node({"question": "질문", "vector_hits": ["조각"]})
    assert generator.last_sufficient is True

    await interactor.generate_answer_node({"question": "질문"})
    assert generator.last_sufficient is False


# ---- 조건부 엣지 (004 하네스 규칙 4) ----

def test_진입_분기는_라우트를_따른다():
    assert route_entry({"route": GRAPH_ROUTE}) == GRAPH_NODE
    assert route_entry({"route": VECTOR_ROUTE}) == VECTOR_NODE
    assert route_entry({}) == VECTOR_NODE


def test_근거가_있으면_생성으로_간다():
    assert decide_after_search({"vector_hits": ["조각"], "retry_count": 1}) == GENERATE_NODE
    assert decide_after_search({"graph_hits": ["관계"], "retry_count": 1}) == GENERATE_NODE


def test_근거가_없고_여력이_있으면_반대편_검색으로_보강한다():
    assert decide_after_search({"route": VECTOR_ROUTE, "retry_count": 0}) == GRAPH_NODE
    assert decide_after_search({"route": GRAPH_ROUTE, "retry_count": 0}) == VECTOR_NODE


def test_재시도_상한에_닿으면_근거가_없어도_생성으로_보낸다():
    state = {"route": VECTOR_ROUTE, "retry_count": MAX_RETRY, "vector_hits": [], "graph_hits": []}

    assert decide_after_search(state) == GENERATE_NODE


def test_어떤_상태에서도_무한_루프가_생기지_않는다():
    '''종료 보장 — 검색이 항상 빈 결과여도 상한에서 반드시 생성 노드로 빠진다.'''
    visited = []
    state = {"route": VECTOR_ROUTE, "retry_count": 0, "vector_hits": [], "graph_hits": []}

    for _ in range(10):
        nxt = decide_after_search(state)
        visited.append(nxt)
        if nxt == GENERATE_NODE:
            break
        state["retry_count"] += 1

    assert visited[-1] == GENERATE_NODE
    assert len(visited) <= MAX_RETRY + 1


def test_근거_충분성_판정():
    assert has_sufficient_evidence({"vector_hits": ["조각"]}) is True
    assert has_sufficient_evidence({"graph_hits": ["관계"]}) is True
    assert has_sufficient_evidence({"vector_hits": [], "graph_hits": []}) is False
    assert has_sufficient_evidence({}) is False
