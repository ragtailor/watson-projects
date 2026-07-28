---
type: spoke
app: silicon_valley
links:
  - star_craft
---

# LangGraph 작업 하네스

Claude가 이 저장소에서 LangGraph 관련 작업을 할 때 지켜야 할 규칙이다.
[003-langchain-harness.md](003-langchain-harness.md)를 대체하지 않고 **보완**한다 — 기존 선형 LangChain 체인은
그대로 유지하면서, 시멘틱 라우터가 "추론(reasoning)"이 필요하다고 판단한 질문만 LangGraph 엔진으로
분기시키는 하네스다.

---

## 0. 컨텍스트

- **현재 파이프라인은 완전한 선형 구조다.** `star_craft.KerriganSemanticChatInteractor`는 Kiwi
  형태소 분석 기반 키워드 스코어링(`kerrigan_intent_map.py`)으로 의도를
  `GREETING`/`FAREWELL`/`SUPPORT`/`SMALL_TALK`/`UNKNOWN` 중 하나로 판단한 뒤, 판단 결과와 무관하게
  항상 동일한 단일 LangChain 체인(`KerriganChatbotEngineClient`: `prompt | llm | parser`)을 호출한다.
  조건 분기·루프·상태 공유가 전혀 없다.
- **`langgraph`는 이미 설치돼 있으나 사용처가 없다.** `requirements.txt`에 `langgraph==0.2.70`이
  있지만, `silicon_valley/app/use_cases/langgraph_interactor.py`는 자리만 잡아둔 빈 파일이다. 이
  하네스가 실제로 채워야 할 대상이 이 파일이다.
- **Neo4j 그래프 DB는 개념만 정리돼 있고 실제 연결이 없다.** [002-neo4j-harness.md](002-neo4j-harness.md)는
  노드/라벨/관계/속성 모델을 설명할 뿐이며, `neo4j-graphrag` 패키지는 현재 PDF 텍스트 추출
  (`GraphPdfExtractor`, `neo4j_graphrag.experimental.components.pdf_loader.PdfLoader`)에만 쓰인다.
  실제 저장소는 Postgres `document_vector` 테이블이다. `Neo4jGraph`/`GraphCypherQAChain` 드라이버
  연결은 이 하네스를 적용하는 시점에 새로 구축해야 하는 영역이다 — "이미 GraphRAG가 있다"고
  가정하지 않는다.
- **라우팅은 hub(`star_craft`)의 책임이다.** 스타 토폴로지 규칙상 `silicon_valley`(spoke)는 다른
  spoke를 임포트할 수 없지만, hub는 오케스트레이션 목적으로 spoke를 직접 임포트할 수 있다
  ([star-003-sementic-harness.md](../../star_craft/_docs/star-003-sementic-harness.md) 참고). 즉
  "reasoning 인텐트면 LangGraph로 위임" 분기는 `star_craft` 쪽 어댑터에 둔다.

---

## 1. 절대 규칙

1. **LangGraph는 기존 인텐트 전부를 대체하지 않는다.** `GREETING`/`FAREWELL`/`SUPPORT`/`SMALL_TALK`는
   여전히 기존 선형 LangChain 체인(`KerriganChatbotEngineClient`)으로 처리한다. LangGraph는 새 인텐트
   카테고리(예: `REASONING`)에만, 그것도 실제로 조건 분기·루프·상태 공유가 필요할 때만 연결한다.
2. **라우팅 분기는 포트 뒤에 숨긴다.** `KerriganSemanticChatInteractor`는 지금처럼
   `KerriganChatbotEnginePort.reply(message, intent)`만 호출하고, 내부적으로 선형 체인과 LangGraph
   중 무엇이 실행되는지 알지 못한다. intent별 분기는 `KerriganChatbotEnginePort` 구현체(어댑터
   계층) 안에서만 이루어지는 Strategy로 둔다 — 인터랙터를 건드리지 않는다.
3. **State는 `TypedDict`로 명시 선언한다.** 대화 메시지뿐 아니라 검색된 문서, 재시도 횟수, 중간
   판단값까지 그래프 전체가 공유·갱신하는 상태에 담는다. 암묵적으로 클로저나 전역 변수로 상태를
   흘리지 않는다.
4. **모든 조건부 엣지는 반드시 `END`로 가는 경로를 보장한다.** 재시도·자기수정(self-correction)
   루프를 만들 때는 상태에 재시도 횟수 필드를 두고, 조건 함수가 이를 확인해 상한에 도달하면 무조건
   종료 경로로 보낸다. 종료 조건 없는 루프는 만들지 않는다.
5. **Neo4j/GraphRAG 조회는 output port 뒤에 둔다.** 그래프 노드 함수가 `Neo4jGraph`,
   `GraphCypherQAChain` 같은 구체 클래스를 직접 참조하지 않는다 — 프로바이더를 포트 뒤에 숨기는
   원칙은 [003-langchain-harness.md](003-langchain-harness.md) 1번 규칙과 동일하다.
6. **spoke → spoke 임포트 금지는 LangGraph 도입 이후에도 그대로 유지된다.** `star_craft`가
   `silicon_valley`의 포트/유즈케이스를 참조하는 것(hub → spoke)은 허용되지만, 역방향
   (`silicon_valley` → `star_craft`) 또는 다른 spoke가 `silicon_valley`를 직접 참조하는 것은 여전히
   금지다. `lint-imports`로 확인한다.

---

## 2. 체크리스트

작업을 완료로 보고하기 전에 아래를 확인한다.

- [ ] **분류 기준:** `REASONING`(또는 새로 정의한 카테고리)의 키워드 집합이 기존
      `SUPPORT`/`SMALL_TALK` 등과 겹쳐 오분류를 유발하지 않는가?
- [ ] **필요성:** 실제로 분기·루프가 있는 그래프인가? 검색 1회 → 생성 1회로 끝난다면 LangGraph
      대신 기존 LCEL 체인을 쓴다 ([003-langchain-harness.md](003-langchain-harness.md) 2번 체크리스트와
      동일한 판단 기준).
- [ ] **종료 보장:** 조건부 엣지마다 `END`로 가는 탈출 경로가 있는가? 재시도 상한이 상태에 있는가?
- [ ] **인프라 선행 확인:** Neo4j 실 연결이 아직 없는 상태라면, [002-neo4j-harness.md](002-neo4j-harness.md)의
      노드/라벨/관계/속성 모델을 먼저 확정한 뒤에 드라이버·포트를 연결했는가?
- [ ] **토폴로지:** `lint-imports`가 통과하는가 (spoke → spoke 직접 임포트가 새로 생기지 않았는가)?

---

## 3. 예상 구현 매핑 (아직 미구현 — 착수 시 참고용 뼈대)

| 영역 | 파일 | 상태 |
| ---- | ---- | ---- |
| 인텐트 분류 | `star_craft/domain/kerrigan_intent_map.py` | `REASONING` 카테고리 키워드 추가 필요 |
| 라우팅 어댑터 | `star_craft/adapter/outbound/client/kerrigan_chatbot_engine_client.py` | intent 분기(선형 체인 ↔ LangGraph 위임)를 위해 교체 또는 신규 라우터 어댑터 추가 필요 |
| LangGraph 출력 포트 | `silicon_valley/app/ports/output/graph_reasoning_port.py` | 신규 |
| LangGraph 인터랙터 | `silicon_valley/app/use_cases/langgraph_interactor.py` | 현재 빈 파일 — `StateGraph` 구현 대상 |
| Neo4j/GraphRAG 어댑터 | `silicon_valley/adapter/outbound/client/graph_reasoning_client.py` | 신규 (Neo4j 드라이버 연결 포함) |

---

## 4. 참고

- 기존 선형 체인 규칙: [003-langchain-harness.md](003-langchain-harness.md)
- 그래프 데이터 모델 개념: [002-neo4j-harness.md](002-neo4j-harness.md)
- 시멘틱 라우팅 구조: [../../star_craft/_docs/star-003-sementic-harness.md](../../star_craft/_docs/star-003-sementic-harness.md)
