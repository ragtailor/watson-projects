from __future__ import annotations

import re

VECTOR_ROUTE = "VECTOR"
GRAPH_ROUTE = "GRAPH"

# 관계·비교·인과를 묻는 질문은 그래프 탐색이, 내용·요약을 묻는 질문은 벡터 검색이 유리하다.
_GRAPH_HINTS = frozenset({
    "관계", "관련", "연관", "연결", "누구", "누가", "소속", "사이",
    "원인", "이유", "때문", "영향", "비교", "차이", "함께", "같이",
})

_STOPWORDS = frozenset({
    "그리고", "하지만", "그래서", "무엇", "어떻게", "얼마나", "알려줘", "설명해줘",
    "해줘", "인가", "인지", "있나", "없나", "대해", "대한", "관해",
})

_TOKEN_RE = re.compile(r"[0-9A-Za-z가-힣]+")


def decide_route(question: str) -> str:
    '''질문 의도를 벡터 검색과 그래프 검색 중 하나로 분류한다.

    LLM을 쓰지 않는 이유는 라우팅 한 번에 추론 호출을 추가하면 지연이 두 배가 되고,
    분기 근거를 테스트로 고정할 수 없기 때문이다. 키워드로 시작해 필요할 때 교체한다.
    '''
    text = question or ""
    if any(hint in text for hint in _GRAPH_HINTS):
        return GRAPH_ROUTE
    return VECTOR_ROUTE


def extract_keywords(question: str, limit: int = 5) -> list[str]:
    '''그래프 조회에 쓸 키워드를 뽑는다. 불용어와 1글자 토큰은 버린다.'''
    keywords: list[str] = []
    for token in _TOKEN_RE.findall(question or ""):
        if len(token) < 2 or token in _STOPWORDS or token in _GRAPH_HINTS:
            continue
        if token not in keywords:
            keywords.append(token)
        if len(keywords) >= limit:
            break

    return keywords
