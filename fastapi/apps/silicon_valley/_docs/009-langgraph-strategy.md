---
type: spoke
app: silicon_valley
links:
  - star_craft
---

# LangGraph 전략 — Pgvector + Neo4j 하이브리드 GraphRAG 에이전트

[004-langgraph-harness.md](004-langgraph-harness.md)가 정의한 절대 규칙 위에, "Pgvector(벡터) + Neo4j(그래프)
하이브리드 검색을 LangGraph 에이전트로 오케스트레이션한다"는 확장 전략을 얹는 문서다.
[008-neo4j-strategy.md](008-neo4j-strategy.md)가 컨테이너·드라이버 연결까지 메웠으므로, 이 문서는 그
드라이버 위에 **지식 그래프 적재 파이프라인**과 **StateGraph 에이전트**를 올리는 계획만 다룬다.

이 문서는 설계 문서다. 코드는 포함하지 않는다. **1~9단계 전부 구현 완료**이며, 산출물과 검증 범위는
[6장](#6-구현-순서)의 두 완료 표에 기록했다. 인프라(Docker·Neo4j·pip)가 필요한 검증은 아직 남아 있다.

---

## 0. 전제 검증 — "기존 Pgvector 유사도 검색"은 이 저장소에 아직 없다

확장 전략의 출발 전제("기존 LangChain + Pgvector 구조가 문장 유사도 기반 검색에 특화되어 있었다")는
저장소 실제 상태와 다르다. 이 격차를 먼저 명시한다. 격차를 모르고 "Neo4j만 더하면 하이브리드가 된다"고
가정하면 하이브리드의 절반(벡터 쪽)이 비어 있는 상태로 에이전트를 짜게 된다.

| 전제 | 저장소 실제 상태 | 근거 |
| ---- | ---------------- | ---- |
| 문서 청크 + 임베딩이 Pgvector에 저장돼 있다 | `silicon_valley_document_vectors` 테이블은 `filename`/`content`/`summary` (모두 `Text`/`String`)뿐 — **벡터 컬럼이 없다** | `adapter/outbound/orm/document_vector_orm.py` |
| 질문과 유사한 청크를 검색한다 | 유사도 검색 코드가 저장소 전체에 **0건** (`cosine_distance`/`l2_distance`/`<->` 사용처 없음) | 전체 `*.py` grep |
| Morningstar가 관련 보고서를 찾아온다 | `find_recent_reports`는 `ORDER BY id DESC LIMIT n` — 최신순이며 유사도와 무관 | `adapter/outbound/repository/morningstar_report_repository.py` |
| 청킹(chunking)이 있다 | PDF 본문 전체를 한 행에 통째로 저장한다 (`extract_text → summarize → save`) | `app/use_cases/graph_pdf_loader_interactor.py` |
| `pgvector`가 안 쓰인다 | 패키지는 설치돼 있고(`pgvector==0.4.1`), `Vector` 컬럼은 `moneyball.player_embedding`(1536), `sherlock_homes.mary_mail_embeddings`(1024)에만 있다 — 둘 다 적재만 하고 검색은 없다 | `requirements.txt`, 각 `*_orm.py` |
| `LLMGraphTransformer`를 쓸 수 있다 | `langchain-experimental` **미설치**. 설치된 그래프 도구는 `neo4j-graphrag`이며 현재 `PdfLoader`(텍스트 추출)에만 쓰인다 | `requirements.txt`, `adapter/outbound/loader/graph_pdf_extractor.py` |

반대로, 008 전략은 이미 **구현 완료** 상태이므로 다시 하지 않는다.

- `docker-compose.yml`의 `neo4j` 서비스 + healthcheck (`cypher-shell ... RETURN 1`)
- `.env.example`의 `NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD`
- `core/matrix/grid_architect_graph_manager.py` (`init_driver` / `get_driver` / `dispose_driver`)
- `main.py` lifespan에 `init_driver()` / `dispose_driver()` 연결

단, `get_driver()`를 **실제로 호출하는 코드는 아직 없다**. 이 문서의 그래프 검색 어댑터가 첫 소비자가 된다.

**결론:** 이 전략은 "벡터 검색에 그래프 검색을 추가"가 아니라, **벡터 검색과 그래프 검색을 둘 다 신규 구축한 뒤
LangGraph로 라우팅**하는 작업이다. 1단계(벡터 검색 완성)를 건너뛰면 하이브리드가 성립하지 않는다.

---

## 1. 확장 3단계와 이 저장소의 대응

| 단계 | 확장 내용 | 이 저장소에서 필요한 작업 |
| ---- | --------- | ------------------------- |
| 개념 | 벡터 = 문장 유사도, 그래프 = 관계 탐색 | — |
| 데이터 | Pgvector + Neo4j 이중 적재 | 청킹·임베딩·유사도 검색 신규 + LLM 엔티티/관계 추출 신규 |
| 에이전트 | `StateGraph`로 판단·분기·루프 | 빈 파일 `app/use_cases/langgraph_interactor.py` 채우기 |

세 단계는 순차 의존이다. 데이터 단계가 비어 있으면 에이전트 단계의 두 검색 노드가 모두 빈 결과를 반환한다.

---

## 2. 데이터 저장소 확장 — 하이브리드 적재 파이프라인

기존 PDF 업로드 파이프라인(`GraphPdfLoaderInteractor`: 추출 → 요약 → 저장)을 **버리지 않고 분기를 추가**한다.

```text
[PDF 업로드]
     │
     ├──► 추출(GraphPdfExtractor) ──► 요약(Gemini) ──► 원문/요약 저장          (기존, 유지)
     │
     ├──► 청킹 ──► 임베딩 ──► Pgvector 청크 테이블 저장                        (신규 — 벡터 검색용)
     │
     └──► LLM 엔티티/관계 추출 ──► Neo4j 노드/관계 저장                        (신규 — 그래프 검색용)
```

### 2.1 벡터 쪽 (신규)

- **테이블 분리:** 기존 `silicon_valley_document_vectors`(문서 1행 = 원문 전체)는 Morningstar가 이미 쓰고 있으므로
  스키마를 바꾸지 않는다. 청크는 별도 테이블(예: `silicon_valley_document_chunks`)에 `document_id`(FK),
  `chunk_index`, `content`, `embedding`으로 둔다. 기존 테이블에 `Vector` 컬럼을 덧붙이면 "문서 = 청크"라는
  모순이 생긴다.
- **임베딩 차원 확정이 선행 조건이다.** 저장소에 이미 1536(moneyball)과 1024(sherlock_homes) 두 규격이
  섞여 있다. `Vector(N)`의 `N`은 마이그레이션 없이 바꿀 수 없으므로, 사용할 임베딩 모델을 먼저 고정하고
  그 모델의 실제 출력 차원으로 컬럼을 만든다.
- **임베딩 경로:** `core/lol/t1_mid_faker_orchestrator.py`의 `FakerOrchestrator.embed()`가 Ollama
  `/api/embeddings`를 호출하는 기존 경로다(`sherlock_homes`가 이 방식을 쓴다). 다만 이 클래스는 채팅 모델
  `exaone3.5:2.4b`를 임베딩에도 그대로 쓰고 `base_url`/`model`이 모듈 상수로 하드코딩돼 있다 —
  [003-langchain-harness.md](003-langchain-harness.md) 규칙 4(모델 교체 지점은 환경 변수)에 어긋난다.
  전용 임베딩 모델명을 환경 변수로 받는 출력 포트를 `silicon_valley` 쪽에 새로 두고, 구현체가 Ollama를
  호출하게 한다.
- **인덱스:** 청크 수가 적은 초기에는 인덱스 없이(순차 스캔) 시작하고, 규모가 커지면 HNSW를 추가한다.
  선제적으로 인덱스를 만들지 않는다.

### 2.2 그래프 쪽 (신규)

- **추출 도구 선택:** `LLMGraphTransformer`(`langchain_experimental.graph_transformers`)를 쓰려면
  `langchain-experimental`을 `requirements.txt`에 추가해야 한다. 이미 설치된 `neo4j-graphrag`의
  엔티티/관계 추출 컴포넌트로도 같은 일이 가능하다. **의존성을 늘리지 않는 후자를 기본안으로 제안**하되,
  둘 중 무엇을 쓸지는 착수 시 확정한다 (아래 [7장](#7-확정이-필요한-결정) 참고).
- **라벨 네임스페이스:** [008-neo4j-strategy.md](008-neo4j-strategy.md) 1장의 결정을 그대로 따른다. 같은
  컨테이너·같은 기본 DB를 쓰되 라벨로 분리한다 — 허브 온톨로지는 `Hub`/`Spoke`, GraphRAG 지식 그래프는
  `Document`/`Entity` 계열. 모든 Cypher는 라벨로 범위를 좁혀 두 그래프가 섞이지 않게 한다.
- **문서 ↔ 그래프 연결:** 추출된 `Entity` 노드는 출처 `Document` 노드와 관계로 연결하고, `Document` 노드
  속성에 Postgres `document_vector.id`를 보관한다. 그래프 검색 결과에서 원문 청크로 되돌아올 수 있어야
  최종 답변에 근거를 붙일 수 있다.
- **비용/시간:** 엔티티 추출은 문서당 LLM 호출이 여러 번 발생한다. 업로드 요청 안에서 동기로 돌리면 응답이
  길어지므로, 초기에는 **관리자용 별도 엔드포인트(또는 스크립트)로 수동 트리거**하고 업로드 경로는 기존
  동작을 유지한다. 자동화는 필요성이 확인된 뒤에 검토한다.

---

## 3. LangGraph 에이전트 설계

004 하네스의 절대 규칙을 그대로 적용한다. 특히 규칙 2(라우팅 분기는 포트 뒤에), 규칙 3(State는 `TypedDict`),
규칙 4(모든 조건부 엣지는 `END` 경로 보장), 규칙 5(그래프 조회는 출력 포트 뒤)를 위반하지 않는다.

### 3.1 그래프 흐름

```text
[사용자 질문]
     │
     ▼
[의도 분석 노드] ──── 관계·연관성 질문 ────► [Neo4j Cypher 검색 노드]
     │                                              │
     └──── 단순 내용·요약 질문 ────► [Pgvector 검색 노드]
                                                    │
     ┌──────────────────────────────────────────────┘
     ▼
[근거 충분성 판단 노드]
     │
     ├── 부족 & 재시도 여력 있음 ──► 아직 안 쓴 검색 노드로 보강 (루프 1회)
     │
     └── 충분 또는 재시도 상한 도달 ──► [답변 생성 노드] ──► END
```

- 두 검색 노드는 **배타적이 아니다.** 첫 검색이 부족하면 다른 검색으로 보강한다. 이 보강 루프가 곧
  LangGraph를 쓰는 이유다 — 단일 검색 후 단일 생성으로 끝난다면 004 하네스 체크리스트대로 기존 LCEL 체인을
  쓰고 LangGraph는 도입하지 않는다.
- **종료 보장:** State에 재시도 횟수 필드를 두고, 충분성 판단 함수가 상한(초기값 1)에 도달하면 근거가
  부족하더라도 무조건 답변 생성 노드로 보낸다. 이때 "근거가 부족하다"는 사실을 답변에 명시한다.

### 3.2 State 스키마 (`TypedDict`)

| 필드 | 용도 |
| ---- | ---- |
| `question` | 사용자 질문 원문 |
| `route` | 의도 분석 결과 (벡터 / 그래프) |
| `vector_hits` | Pgvector 검색으로 얻은 청크 목록 |
| `graph_hits` | Neo4j 검색으로 얻은 관계망 요약 |
| `retry_count` | 보강 루프 횟수 — 상한 비교용 |
| `answer` | 최종 생성 답변 |

대화 이력은 이 State에 넣지 않는다. 대화 저장은 hub의 `KerriganConversationRepository` 책임이며, 지금 단계의
에이전트는 단일 질문 처리로 범위를 한정한다.

### 3.3 Cypher 생성 방식

자연어 → Cypher 자동 생성(`GraphCypherQAChain` 계열)은 임의 쿼리를 LLM이 만들게 하므로, 라벨 네임스페이스가
섞이거나 그래프 전체를 스캔하는 쿼리가 나올 수 있다. **1차 구현은 파라미터만 LLM이 채우는 고정 Cypher 템플릿
몇 개**로 시작한다. 자유 생성은 템플릿으로 커버되지 않는 질문 유형이 실제로 확인된 뒤 검토한다.

### 3.4 hub 라우팅과의 접점

004 하네스 규칙 1·2를 유지한다.

- `GREETING`/`FAREWELL`/`SUPPORT`/`SMALL_TALK`는 계속 기존 선형 체인(`KerriganChatbotEngineClient`)이 처리한다.
- `star_craft/domain/kerrigan_intent_map.py`에 `REASONING` 카테고리를 추가한다. 현재 이 맵은 위 4개
  카테고리만 가지며, 동점 시 **삽입 순서가 우선순위**이므로 `REASONING`을 어디에 넣는지가 오분류에
  직결된다. 키워드는 `SUPPORT`의 문의/오류 계열과 겹치지 않게 관계·비교·인과 계열로 좁힌다.
- `KerriganChatbotEnginePort.reply(message, intent)` 시그니처는 바꾸지 않는다. intent별 분기(선형 체인 ↔
  LangGraph 위임)는 hub의 어댑터 계층 안에서만 이루어진다. `KerriganSemanticChatInteractor`는 수정하지 않는다.

---

## 4. 레이어 매핑 (구현 완료 — 실제 파일명은 6장 완료 표 참고)

`silicon_valley` 네이밍 컨벤션은 파이드 파이퍼 인물명 접두어(`piper_gilfoyle_*`, `piper_dinesh_*`,
`piper_dunn_*`, `piper_bighetti_*`, `piper_henricks_*`)를 쓴다. 이 슬라이스는 `monica`로 확정했다.
[001-silicon-valley-casting.md](001-silicon-valley-casting.md)는 여전히 빈 파일이므로 전체 캐스팅 문서화는
별도 과제로 남는다.

아래 초안과 실제 구현의 차이: 청크 리포지터리 포트는 `knowledge_chunk_repository_port.py`로,
답변 생성 포트는 `piper_monica_answer_generator_port.py`로 두고, 문서 단건 조회용
`document_reader_port.py`와 라우팅 도메인 로직 `domain/reasoning_route.py`가 추가되었다.

```text
domain/knowledge_chunk.py                                          # 신규: 청크 엔티티 (id, document_id, content)
domain/knowledge_graph_fact.py                                     # 신규: 그래프 조회 결과 (엔티티·관계 튜플)
app/dtos/piper_monica_graph_dto.py                                 # Query / Response
app/ports/input/piper_monica_graph_use_case.py                     # 하이브리드 질의 입력 포트
app/ports/output/knowledge_chunk_repository_port.py                # Pgvector 유사도 검색
app/ports/output/knowledge_embedder_port.py                        # 텍스트 → 임베딩
app/ports/output/graph_reasoning_port.py                            # Neo4j Cypher 조회 (004 매핑과 동일 이름)
app/ports/output/piper_monica_answer_generator_port.py             # 최종 답변 생성 (LLM)
app/use_cases/langgraph_interactor.py                              # 현재 빈 파일 — StateGraph 조립 대상
adapter/outbound/orm/knowledge_chunk_orm.py                        # Vector(N) 컬럼 보유
adapter/outbound/repository/knowledge_chunk_repository.py          # pgvector 거리 연산자 사용
adapter/outbound/client/knowledge_embedder_client.py               # Ollama 임베딩 (모델명 환경 변수)
adapter/outbound/client/graph_reasoning_client.py                   # get_driver()로 세션 열기
adapter/outbound/client/knowledge_graph_ingest_client.py           # 엔티티/관계 추출 → Neo4j 적재
adapter/inbound/api/schemas/piper_monica_graph_schema.py
adapter/inbound/api/v1/piper_monica_graph_router.py                # POST /silicon-valley/monica/ask
dependencies/piper_monica_graph_provider.py
```

`langgraph_interactor.py`는 노드 함수들을 조립하는 역할만 맡고, 각 노드 함수는 위 출력 포트만 의존한다.
`Neo4jGraph`, `GraphCypherQAChain`, `ChatOllama` 같은 구체 클래스는 `adapter/outbound/` 밖으로 나오지 않는다.

---

## 5. 검증 절차

| 대상 | 검증 방법 | 통과 기준 |
| ---- | --------- | --------- |
| 임베딩 차원 | 임베딩 포트를 1회 호출해 길이 확인 | `Vector(N)`의 `N`과 실제 출력 길이가 일치 |
| 벡터 검색 | 적재한 청크의 원문 일부를 그대로 질의 | 해당 청크가 1위로 반환 |
| 그래프 적재 | `MATCH (e:Entity) RETURN count(e)` | 0이 아니고, `Document`와 관계로 연결돼 있음 |
| 라벨 격리 | `MATCH (n:Hub|Spoke) ... ` / `MATCH (n:Entity) ...` 각각 실행 | 두 결과 집합이 겹치지 않음 |
| 종료 보장 | 검색 결과가 항상 비도록 스텁을 넣고 실행 | 재시도 상한에서 멈추고 `END`에 도달 (무한 루프 없음) |
| 라우팅 | `REASONING` 키워드 추가 후 기존 4개 인텐트 질문 재확인 | 기존 인텐트 분류가 바뀌지 않음 |
| 토폴로지 | `cd fastapi && lint-imports` | spoke → spoke 직접 임포트 0건 |
| 온톨로지 | `markdownlint "**/_docs/**/*.md"` + `python scripts/validate_harness.py` | 둘 다 통과 |

단위 테스트는 DB·Neo4j·Ollama 없이 돌아야 한다(루트 CLAUDE.md 테스트 규칙). 노드 함수와 조건 함수는 포트를
가짜 구현으로 주입해 검증하고, 실제 인프라가 필요한 항목은 위 표의 수동 절차로 확인한다.

---

## 6. 구현 순서

```text
1. 임베딩 모델·차원 확정                        → 검증: embed() 출력 길이 == 선언한 N
2. 청크 테이블 ORM + 마이그레이션                → 검증: alembic upgrade head 성공
3. 청킹·임베딩 적재 경로 추가                    → 검증: 업로드 후 청크 행 수 > 0
4. Pgvector 유사도 검색 리포지터리               → 검증: 원문 질의 시 해당 청크 1위 (5장 표)
5. 엔티티/관계 추출 + Neo4j 적재 어댑터          → 검증: Entity 노드 수 > 0, Document와 연결됨
6. 고정 Cypher 템플릿 기반 그래프 조회 어댑터     → 검증: 라벨 격리 쿼리 통과
7. StateGraph 조립 (노드 + 조건부 엣지)          → 검증: 빈 결과 스텁으로 종료 보장 확인
8. REASONING 인텐트 + hub 라우팅 어댑터 분기      → 검증: 기존 4개 인텐트 분류 불변
9. 라우터·스키마·프로바이더 배선                  → 검증: lint-imports + markdownlint + validate_harness
```

1~4단계만으로도 "유사도 기반 문서 질의"라는 독립적인 가치가 생긴다. 5단계 이후를 나중으로 미루더라도 4단계에서
멈출 수 있게 순서를 잡았다.

### 1~4단계 구현 완료 (2026-07-30)

| 단계 | 산출물 | 검증 결과 |
| ---- | ------ | --------- |
| 1 | `app/ports/output/knowledge_embedder_port.py`, `adapter/outbound/client/knowledge_embedder_client.py` | `nomic-embed-text` 실측 출력 길이 **768** == `EMBEDDING_DIM` |
| 2 | `domain/knowledge_chunk.py`, `adapter/outbound/orm/knowledge_chunk_orm.py`, `alembic/versions/a1c4f7e2b930_*` | 마이그레이션 작성 완료 — `alembic upgrade head`는 DB 접속이 필요해 미실행 |
| 3 | `GraphPdfLoaderInteractor._ingest_chunks`, `KnowledgeChunkRepositoryPort` | 유즈케이스 단위 테스트 6개 통과 (조각 수 > 0, 임베딩 1:1, `chunk_index` 순차) |
| 4 | `adapter/outbound/repository/knowledge_chunk_repository.py` | 실제 Ollama 임베딩으로 코사인 거리 순위 확인 — 원문 발췌 질의가 해당 조각 1위 (거리 0.0181 vs 차순위 0.2449) |

**임베딩 모델 결정 근거 (7장 1번 해소):** 채팅 모델과 분리했다. `exaone3.5:2.4b`는 이 프로젝트의 Ollama
호스트에서 `/api/embeddings`를 제공하지 않으며(completion 모델은 임베딩 모드로 기동되지 않음), 추가로
`OLLAMA_KV_CACHE_TYPE=q4_0` 설정과 EXAONE의 head 차원 80이 충돌해 모델 로드 자체가 실패한다
(`K cache type q4_0 with block size 32 does not divide n_embd_head_k=80`). 따라서 채팅은 `OLLAMA_MODEL`,
임베딩은 `OLLAMA_EMBED_MODEL`(기본 `nomic-embed-text`, 274MB)로 각각 둔다.

**기존 코드 결함 (이 문서 범위 밖, 미수정):** `sherlock_homes`의 `mary_mail_embeddings.embedding`은
`Vector(1024)`로 선언돼 있으나 채팅 모델(`FakerOrchestrator.embed`)로 임베딩한다. 위 제약 때문에 이 경로는
현재 동작하지 않으며, 차원도 실제 출력과 일치하지 않는다.

### 5~9단계 구현 완료 (2026-07-30)

| 단계 | 산출물 | 검증 결과 |
| ---- | ------ | --------- |
| 5 | `domain/knowledge_graph_fact.py`, `app/ports/output/knowledge_graph_{extractor,repository}_port.py`, `adapter/outbound/client/knowledge_graph_extractor_client.py`, `adapter/outbound/repository/knowledge_graph_repository.py`, `app/use_cases/knowledge_graph_ingest_interactor.py` | 파서 단위 테스트 9개 통과. **Neo4j 실 적재는 미검증** — 이 환경에 Docker가 없어 `Entity` 노드 수 > 0을 확인할 수 없다 |
| 6 | `app/ports/output/graph_reasoning_port.py`, `adapter/outbound/client/graph_reasoning_client.py` | **미검증** — 라벨 격리 쿼리는 Neo4j 인스턴스가 필요하다. Cypher 문법도 실행으로 확인되지 않았다 |
| 7 | `app/use_cases/langgraph_interactor.py` (빈 파일이었음) | 노드·조건부 엣지 단위 테스트 10개 통과. 빈 결과 스텁으로 **종료 보장 확인**(무한 루프 없음). `build_graph()`의 `StateGraph` 컴파일은 `langgraph` 미설치로 미실행 |
| 8 | `star_craft/domain/kerrigan_intent_map.py`(`REASONING` 추가), `star_craft/adapter/outbound/client/kerrigan_engine_router_client.py` | `KerriganSemanticChatInteractor` 무수정 확인. 기존 4개 인텐트 분류 불변 여부는 Kiwi 필요로 **미검증** |
| 9 | `piper_monica_graph_{router,schema,provider,dto}`, `app/ports/output/document_reader_port.py` | `silicon_valley` → 다른 spoke/hub 임포트 0건 (grep). `lint-imports`·`markdownlint`는 미설치로 미실행 |

**추출 도구 결정 (7장 2번 해소 — 기본안에서 벗어남):** `neo4j-graphrag`의 엔티티 추출 파이프라인 대신
Gemini 프롬프트 + `domain.parse_extraction`(순수 JSON 파서)을 쓴다. 의존성을 늘리지 않고 같은 결과를 얻으며,
파싱 규칙(관계 정규화, 고아 관계 제거, 코드펜스 처리)을 단위 테스트로 고정할 수 있다.

**설계 결정 두 가지:**

- **`Entity` 단일 라벨 + `label` 속성.** 엔티티 종류를 동적 라벨로 만들지 않고 속성에 담는다. 008 1장의
  라벨 네임스페이스 격리를 단순하게 유지하고, 6장의 고정 Cypher가 `MATCH (s:Entity)` 하나로 끝난다.
- **추론 경로 실패 시 선형 체인으로 내려앉는다.** Neo4j·pgvector·임베딩 중 하나가 죽으면 챗봇 전체가
  멈추므로, 라우터 어댑터가 예외를 잡아 기존 체인에 위임한다. 004 규칙 1(기존 인텐트 보호)의 연장이다.

### 남은 검증 (인프라 필요)

```text
1. docker compose --profile local-db up -d pgvector  → alembic upgrade head
2. docker compose up -d neo4j                        → POST /monica/ingest/{id} 후
                                                        MATCH (e:Entity) RETURN count(e)
3. ollama pull nomic-embed-text + exaone3.5:2.4b     → POST /monica/ask 왕복
4. pip install -r requirements.txt                   → pytest, lint-imports, markdownlint
```

---

## 7. 확정이 필요한 결정

착수 전에 답이 필요했던 항목이다. 5개 모두 해소되어 기록만 남긴다.

1. ~~**임베딩 모델**~~ — **해소됨.** `nomic-embed-text`(768). 근거는 6장 "1~4단계 구현 완료" 참고.
2. ~~**엔티티 추출 도구**~~ — **해소됨.** Gemini 프롬프트 + 도메인 JSON 파서. 근거는 6장 "5~9단계 구현 완료" 참고.
3. ~~**추출 LLM**~~ — **해소됨.** Gemini (요약이 이미 Gemini 경로).
4. ~~**적재 트리거**~~ — **해소됨.** 관리자 엔드포인트 `POST /silicon-valley/monica/ingest/{document_id}`로 분리.
   업로드 경로는 기존 동작을 유지한다.
5. ~~**캐스팅**~~ — **해소됨.** `monica` (`piper_monica_*`).

---

## 8. 참고

- [004-langgraph-harness.md](004-langgraph-harness.md) — LangGraph 절대 규칙·체크리스트
- [008-neo4j-strategy.md](008-neo4j-strategy.md) — Neo4j 컨테이너·드라이버 연결 (구현 완료)
- [003-langchain-harness.md](003-langchain-harness.md) — LLM 프로바이더 포트화, 모델 교체 지점 환경 변수화
- [002-neo4j-harness.md](002-neo4j-harness.md) — 노드/라벨/관계/속성 모델
- [../../star_craft/_docs/star-003-sementic-harness.md](../../star_craft/_docs/star-003-sementic-harness.md) —
  시멘틱 라우팅 구조
- [GraphRAG Tutorial — Neo4j + LLMs](https://www.youtube.com/watch?v=odtGLUPXqfs)
