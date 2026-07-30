from __future__ import annotations

from core.matrix.vault_keymaker_secret_manager import get_keymaker

from silicon_valley.app.ports.output.knowledge_graph_extractor_port import KnowledgeGraphExtractorPort
from silicon_valley.domain.knowledge_graph_fact import KnowledgeGraphFacts, parse_extraction

# 요약이 이미 Gemini 경로(GraphDocumentSummarizerClient)이므로 추출도 같은 경로를 쓴다.
# neo4j-graphrag의 파이프라인을 쓰지 않는 이유는 의존성 대비 이득이 없기 때문이다 —
# 프롬프트 한 개와 JSON 파싱(domain.parse_extraction)으로 같은 결과를 얻는다.
_EXTRACTION_PROMPT = """다음 문서에서 지식 그래프를 만들 엔티티와 관계를 추출해라.

규칙:
- 오직 JSON만 출력한다. 설명·코드펜스·주석을 붙이지 않는다.
- entities[].name 은 문서에 등장한 표기를 그대로 쓴다.
- entities[].label 은 Person, Organization, Product, Event, Concept 중 하나를 고른다.
- relations[].type 은 동사구를 대문자 언더스코어로 쓴다 (예: WORKS_AT, CAUSED).
- relations[].source 와 target 은 반드시 entities 에 있는 name 이어야 한다.
- 문서에 근거가 없는 관계는 만들지 않는다.

출력 형식:
{{"entities": [{{"name": "...", "label": "..."}}],
  "relations": [{{"source": "...", "target": "...", "type": "..."}}]}}

문서:
{text}
"""

# 문서 전체를 넣으면 토큰 한도를 넘기기 쉬워 앞부분만 사용한다.
_MAX_CHARS = 12000


class KnowledgeGraphExtractorClient(KnowledgeGraphExtractorPort):
    '''Gemini로 본문에서 엔티티·관계를 추출한다.'''

    def __init__(self, max_chars: int = _MAX_CHARS) -> None:
        self._keymaker = get_keymaker()
        self.max_chars = max_chars

    async def extract(self, text: str) -> KnowledgeGraphFacts:
        model = self._keymaker.get_gemini_model()
        if model is None:
            raise RuntimeError("GEMINI_API_KEY가 설정되지 않아 엔티티를 추출할 수 없습니다.")

        prompt = _EXTRACTION_PROMPT.format(text=text[: self.max_chars])
        response = await model.generate_content_async(prompt)

        return parse_extraction(response.text)
