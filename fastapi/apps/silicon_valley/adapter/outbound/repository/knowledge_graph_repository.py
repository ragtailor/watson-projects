from __future__ import annotations

from neo4j import AsyncDriver

from silicon_valley.app.ports.output.knowledge_graph_repository_port import KnowledgeGraphRepositoryPort
from silicon_valley.domain.knowledge_graph_fact import KnowledgeGraphFacts

# 008-neo4j-strategy.md 1장의 라벨 네임스페이스 결정을 따른다.
# 허브 온톨로지(Hub/Spoke)와 같은 DB를 공유하므로 모든 쿼리를 이 라벨로 좁힌다.
_MERGE_DOCUMENT = """
MERGE (d:Document {postgres_id: $document_id})
SET d.filename = $filename
"""

_MERGE_ENTITY = """
MERGE (e:Entity {name: $name})
SET e.label = $label
WITH e
MATCH (d:Document {postgres_id: $document_id})
MERGE (d)-[:MENTIONS]->(e)
"""

# 관계 타입은 Cypher에서 파라미터화할 수 없어 문자열로 합성한다.
# 도메인의 _normalize_relation_type이 영숫자·언더스코어만 남기므로 주입 위험은 없다.
_MERGE_RELATION = """
MATCH (s:Entity {{name: $source}}), (t:Entity {{name: $target}})
MERGE (s)-[r:{rel_type}]->(t)
SET r.document_id = $document_id
"""


class KnowledgeGraphRepository(KnowledgeGraphRepositoryPort):
    '''추출된 엔티티·관계를 Neo4j에 MERGE로 적재한다 (재실행 시 중복 생성 없음).'''

    def __init__(self, driver: AsyncDriver) -> None:
        self.driver = driver

    async def ingest(self, document_id: int, filename: str, facts: KnowledgeGraphFacts) -> int:
        if facts.is_empty():
            return 0

        async with self.driver.session() as session:
            await session.run(_MERGE_DOCUMENT, document_id=document_id, filename=filename)

            for entity in facts.entities:
                await session.run(
                    _MERGE_ENTITY,
                    name=entity.name,
                    label=entity.label,
                    document_id=document_id,
                )

            for relation in facts.relations:
                await session.run(
                    _MERGE_RELATION.format(rel_type=relation.type),
                    source=relation.source,
                    target=relation.target,
                    document_id=document_id,
                )

        return len(facts.entities)
