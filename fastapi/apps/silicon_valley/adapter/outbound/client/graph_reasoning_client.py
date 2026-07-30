from __future__ import annotations

from neo4j import AsyncDriver

from silicon_valley.app.ports.output.graph_reasoning_port import GraphReasoningPort

# 009 문서 3.3의 결정: 자연어 → Cypher 자유 생성을 쓰지 않는다.
# LLM이 임의 쿼리를 만들면 라벨 네임스페이스가 섞이거나 그래프 전체를 스캔할 수 있다.
# 파라미터만 채우는 고정 템플릿으로 시작하고, 라벨은 항상 Entity로 좁힌다.
_FIND_RELATED = """
UNWIND $keywords AS keyword
MATCH (s:Entity)-[r]->(t:Entity)
WHERE toLower(s.name) CONTAINS toLower(keyword)
   OR toLower(t.name) CONTAINS toLower(keyword)
RETURN DISTINCT s.name AS source, type(r) AS relation, t.name AS target
LIMIT $limit
"""


class GraphReasoningClient(GraphReasoningPort):
    '''고정 Cypher 템플릿으로 Entity 관계망을 조회한다.'''

    def __init__(self, driver: AsyncDriver) -> None:
        self.driver = driver

    async def find_related(self, keywords: list[str], limit: int) -> list[str]:
        cleaned = [k.strip() for k in keywords if k and k.strip()]
        if not cleaned:
            return []

        async with self.driver.session() as session:
            result = await session.run(_FIND_RELATED, keywords=cleaned, limit=limit)
            records = [record.data() async for record in result]

        return [
            f"{r['source']} -[{r['relation']}]-> {r['target']}"
            for r in records
        ]
