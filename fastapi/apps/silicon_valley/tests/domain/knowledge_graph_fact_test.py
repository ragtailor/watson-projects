import pytest

from silicon_valley.domain.knowledge_graph_fact import parse_extraction
from silicon_valley.domain.reasoning_route import (
    GRAPH_ROUTE,
    VECTOR_ROUTE,
    decide_route,
    extract_keywords,
)

_VALID = """
{"entities": [{"name": "길포일", "label": "Person"},
              {"name": "파이드 파이퍼", "label": "Organization"}],
 "relations": [{"source": "길포일", "target": "파이드 파이퍼", "type": "works at"}]}
"""


def test_정상_JSON에서_엔티티와_관계를_파싱한다():
    facts = parse_extraction(_VALID)

    assert [e.name for e in facts.entities] == ["길포일", "파이드 파이퍼"]
    assert facts.entities[0].label == "Person"
    assert len(facts.relations) == 1


def test_관계_타입은_대문자_언더스코어로_정규화된다():
    facts = parse_extraction(_VALID)

    assert facts.relations[0].type == "WORKS_AT"


def test_코드펜스로_감싼_응답도_파싱한다():
    facts = parse_extraction(f"```json\n{_VALID}\n```")

    assert len(facts.entities) == 2


def test_엔티티에_없는_관계는_버린다():
    payload = """
    {"entities": [{"name": "길포일", "label": "Person"}],
     "relations": [{"source": "길포일", "target": "없는사람", "type": "KNOWS"}]}
    """

    facts = parse_extraction(payload)

    assert facts.relations == []
    assert len(facts.entities) == 1


def test_label이_없으면_Entity로_채운다():
    facts = parse_extraction('{"entities": [{"name": "모니카"}]}')

    assert facts.entities[0].label == "Entity"


def test_중복_엔티티는_한_번만_남는다():
    payload = '{"entities": [{"name": "모니카"}, {"name": "모니카", "label": "Person"}]}'

    facts = parse_extraction(payload)

    assert len(facts.entities) == 1


def test_빈_응답은_빈_결과다():
    assert parse_extraction("").is_empty()
    assert parse_extraction("   ").is_empty()


def test_JSON이_아니면_거부한다():
    with pytest.raises(ValueError):
        parse_extraction("엔티티를 찾을 수 없습니다")


def test_JSON_객체가_아니면_거부한다():
    with pytest.raises(ValueError):
        parse_extraction('["길포일"]')


@pytest.mark.parametrize("question", [
    "길포일과 파이드 파이퍼의 관계가 어떻게 돼?",
    "침몰의 원인이 무엇이야",
    "두 회사를 비교해줘",
])
def test_관계_인과_비교_질문은_그래프로_라우팅한다(question):
    assert decide_route(question) == GRAPH_ROUTE


@pytest.mark.parametrize("question", [
    "타이타닉 생존자는 몇 명이야",
    "보고서 내용을 요약해줘",
])
def test_내용_질문은_벡터로_라우팅한다(question):
    assert decide_route(question) == VECTOR_ROUTE


def test_키워드에서_불용어와_한글자를_버린다():
    keywords = extract_keywords("길포일과 모니카의 관계에 대해 알려줘")

    assert "길포일과" in keywords
    assert "관계" not in keywords
    assert "알려줘" not in keywords
    assert all(len(k) >= 2 for k in keywords)


def test_키워드_개수는_상한을_넘지_않는다():
    keywords = extract_keywords("가가 나나 다다 라라 마마 바바 사사", limit=3)

    assert len(keywords) == 3
