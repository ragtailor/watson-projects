from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

# LLM이 코드 펜스로 감싸 반환하는 경우가 흔해 벗겨낸다.
_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)


@dataclass(frozen=True)
class GraphEntity:
    '''지식 그래프의 노드. name은 MERGE 키이므로 공백을 제거해 정규화한다.'''

    name: str
    label: str


@dataclass(frozen=True)
class GraphRelation:
    '''두 엔티티를 잇는 관계. type은 Cypher 관계 타입으로 쓰이므로 대문자·언더스코어로 정규화한다.'''

    source: str
    target: str
    type: str


@dataclass(frozen=True)
class KnowledgeGraphFacts:

    entities: list[GraphEntity] = field(default_factory=list)
    relations: list[GraphRelation] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not self.entities and not self.relations


def _normalize_relation_type(raw: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z가-힣]+", "_", raw.strip()).strip("_")
    return cleaned.upper()


def parse_extraction(payload: str) -> KnowledgeGraphFacts:
    '''LLM의 추출 결과(JSON 문자열)를 도메인 객체로 변환한다.

    관계는 양 끝 엔티티가 모두 추출 목록에 있을 때만 인정한다. 그래야 Cypher MERGE 시
    고아 노드가 생기지 않고, 라벨 없는 노드가 그래프에 섞이지 않는다.
    '''
    fenced = _FENCE_RE.match(payload or "")
    text = fenced.group(1) if fenced else (payload or "")
    text = text.strip()
    if not text:
        return KnowledgeGraphFacts()

    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"추출 결과가 JSON이 아닙니다: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError("추출 결과는 JSON 객체여야 합니다.")

    entities: list[GraphEntity] = []
    seen: set[str] = set()
    for item in raw.get("entities") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        label = str(item.get("label", "")).strip() or "Entity"
        if not name or name in seen:
            continue
        seen.add(name)
        entities.append(GraphEntity(name=name, label=label))

    relations: list[GraphRelation] = []
    for item in raw.get("relations") or []:
        if not isinstance(item, dict):
            continue
        source = str(item.get("source", "")).strip()
        target = str(item.get("target", "")).strip()
        rel_type = _normalize_relation_type(str(item.get("type", "")))
        if not source or not target or not rel_type:
            continue
        if source not in seen or target not in seen:
            continue
        relations.append(GraphRelation(source=source, target=target, type=rel_type))

    return KnowledgeGraphFacts(entities=entities, relations=relations)
