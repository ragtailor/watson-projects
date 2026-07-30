from __future__ import annotations

from typing import Any, TypedDict

from silicon_valley.app.dtos.piper_monica_graph_dto import MonicaAskQuery, MonicaAskResponse
from silicon_valley.app.ports.input.piper_monica_graph_use_case import PiperMonicaGraphUseCase
from silicon_valley.app.ports.output.graph_reasoning_port import GraphReasoningPort
from silicon_valley.app.ports.output.knowledge_chunk_repository_port import KnowledgeChunkRepositoryPort
from silicon_valley.app.ports.output.knowledge_embedder_port import KnowledgeEmbedderPort
from silicon_valley.app.ports.output.piper_monica_answer_generator_port import (
    PiperMonicaAnswerGeneratorPort,
)
from silicon_valley.domain.reasoning_route import GRAPH_ROUTE, VECTOR_ROUTE, decide_route, extract_keywords

# 004 하네스 규칙 4 — 보강 루프 상한. 상한에 닿으면 근거가 부족해도 무조건 답변 생성으로 보낸다.
MAX_RETRY = 1

# 조건부 엣지가 돌려주는 다음 노드 이름. 문자열 오타를 막기 위해 상수로 둔다.
VECTOR_NODE = "vector_search"
GRAPH_NODE = "graph_search"
GENERATE_NODE = "generate_answer"


class ReasoningState(TypedDict, total=False):
    '''004 하네스 규칙 3 — 그래프 전체가 공유·갱신하는 상태를 명시 선언한다.

    대화 이력은 넣지 않는다. 대화 저장은 hub(star_craft)의 책임이며 이 에이전트는
    단일 질문 처리로 범위를 한정한다 (009 문서 3.2).
    '''

    question: str
    top_k: int
    route: str
    vector_hits: list[str]
    graph_hits: list[str]
    retry_count: int
    answer: str


def has_sufficient_evidence(state: ReasoningState) -> bool:
    '''근거 충분성 판단. 어느 한쪽 검색이라도 결과가 있으면 충분으로 본다.'''
    return bool(state.get("vector_hits") or state.get("graph_hits"))


def decide_after_search(state: ReasoningState) -> str:
    '''조건부 엣지 — 근거가 부족하고 재시도 여력이 있으면 아직 안 쓴 검색으로 보강한다.

    상한 도달 시 반드시 생성 노드로 보내므로 모든 경로가 END에 도달한다.
    '''
    if has_sufficient_evidence(state):
        return GENERATE_NODE
    if state.get("retry_count", 0) >= MAX_RETRY:
        return GENERATE_NODE

    return GRAPH_NODE if state.get("route") == VECTOR_ROUTE else VECTOR_NODE


def route_entry(state: ReasoningState) -> str:
    '''진입 분기 — 의도 분석 결과에 따라 첫 검색 노드를 고른다.'''
    return GRAPH_NODE if state.get("route") == GRAPH_ROUTE else VECTOR_NODE


class LangGraphReasoningInteractor(PiperMonicaGraphUseCase):
    '''Pgvector + Neo4j 하이브리드 검색을 LangGraph StateGraph로 오케스트레이션한다.

    노드 함수는 출력 포트만 의존한다 (004 하네스 규칙 5) — Neo4j 드라이버나 LangChain
    구체 클래스가 이 모듈에 등장하지 않는다.
    '''

    def __init__(
        self,
        embedder: KnowledgeEmbedderPort,
        chunk_repository: KnowledgeChunkRepositoryPort,
        graph_reasoning: GraphReasoningPort,
        answer_generator: PiperMonicaAnswerGeneratorPort,
    ) -> None:
        self.embedder = embedder
        self.chunk_repository = chunk_repository
        self.graph_reasoning = graph_reasoning
        self.answer_generator = answer_generator
        self._graph: Any = None

    # ---- 노드 함수 (langgraph 없이도 단위 테스트 가능) ----

    async def analyze_intent_node(self, state: ReasoningState) -> ReasoningState:
        return {"route": decide_route(state["question"]), "retry_count": 0}

    async def vector_search_node(self, state: ReasoningState) -> ReasoningState:
        embedding = await self.embedder.embed(state["question"])
        chunks = await self.chunk_repository.search_similar(
            embedding=embedding,
            limit=state.get("top_k", 4),
        )

        return {
            "vector_hits": [chunk.content for chunk in chunks],
            "retry_count": state.get("retry_count", 0) + 1,
        }

    async def graph_search_node(self, state: ReasoningState) -> ReasoningState:
        keywords = extract_keywords(state["question"])
        hits = await self.graph_reasoning.find_related(
            keywords=keywords,
            limit=state.get("top_k", 4),
        )

        return {
            "graph_hits": hits,
            "retry_count": state.get("retry_count", 0) + 1,
        }

    async def generate_answer_node(self, state: ReasoningState) -> ReasoningState:
        answer = await self.answer_generator.generate(
            question=state["question"],
            vector_hits=state.get("vector_hits", []),
            graph_hits=state.get("graph_hits", []),
            evidence_sufficient=has_sufficient_evidence(state),
        )

        return {"answer": answer}

    # ---- 그래프 조립 ----

    def build_graph(self) -> Any:
        '''StateGraph를 조립해 컴파일한다.

        langgraph를 함수 안에서 임포트하는 이유는 노드 함수 단위 테스트가 이 패키지
        설치 없이도 돌아야 하기 때문이다 (테스트는 DB·LLM·langgraph에 의존하지 않는다).
        '''
        from langgraph.graph import END, StateGraph

        builder = StateGraph(ReasoningState)
        builder.add_node("analyze_intent", self.analyze_intent_node)
        builder.add_node(VECTOR_NODE, self.vector_search_node)
        builder.add_node(GRAPH_NODE, self.graph_search_node)
        builder.add_node(GENERATE_NODE, self.generate_answer_node)

        builder.set_entry_point("analyze_intent")
        builder.add_conditional_edges(
            "analyze_intent",
            route_entry,
            {VECTOR_NODE: VECTOR_NODE, GRAPH_NODE: GRAPH_NODE},
        )
        for search_node in (VECTOR_NODE, GRAPH_NODE):
            builder.add_conditional_edges(
                search_node,
                decide_after_search,
                {
                    VECTOR_NODE: VECTOR_NODE,
                    GRAPH_NODE: GRAPH_NODE,
                    GENERATE_NODE: GENERATE_NODE,
                },
            )
        builder.add_edge(GENERATE_NODE, END)

        return builder.compile()

    async def ask(self, query: MonicaAskQuery) -> MonicaAskResponse:
        if self._graph is None:
            self._graph = self.build_graph()

        final: ReasoningState = await self._graph.ainvoke({
            "question": query.question,
            "top_k": query.top_k,
        })

        return MonicaAskResponse(
            question=query.question,
            route=final.get("route", VECTOR_ROUTE),
            answer=final.get("answer", ""),
            vector_hits=final.get("vector_hits", []),
            graph_hits=final.get("graph_hits", []),
            retry_count=final.get("retry_count", 0),
        )
