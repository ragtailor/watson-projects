---
type: spoke
app: silicon_valley
links:
  - star_craft
---

# LangChain 전략 — NCL: 최적화된 여행 계획 제공

LangChain은 사용자 맞춤형 프롬프팅 및 파인튜닝 기능을 통해 특정 산업의 요구에 맞춘 솔루션을
제공합니다. NCL(노르웨이 크루즈 라인)은 LangChain을 이용해 고객들이 이상적인 크루즈 여행을
계획할 수 있도록 돕는 AI 어시스턴트를 개발했습니다. 이 시스템은 고객의 선호도와 탐색 기록을
기반으로 맞춤형 추천을 제공하며, LangChain을 통해 실시간으로 변화하는 고객 요구에 대응할 수
있습니다.

## 전략 설계

[003-langchain-harness.md](003-langchain-harness.md)의 절대 규칙을 그대로 따라, Morningstar
인사이트 엔진([005-langchain-morningstar-strategy.md](005-langchain-morningstar-strategy.md))과
동일한 구조로 설계한다. 다른 점은 "재무 보고서" 대신 "고객 선호도·탐색 기록"이 실시간 컨텍스트가
된다는 것뿐이다.

| 전략 요소 | 설계 |
| --------- | ---- |
| 고객 선호도·탐색 기록 기반 맞춤형 추천 | `CustomerProfile` 도메인 엔티티(선호 목적지, 선실 등급, 예산, 과거 탐색·예약 이력)를 컨텍스트로 사용 |
| 실시간으로 변화하는 고객 요구 대응 | `NclCustomerProfileRepository`가 매 요청마다 최신 탐색 기록·선호도를 DB에서 조회 (하네스 규칙 3 — 캐시 금지) |
| 맞춤형 프롬프팅 | `ChatPromptTemplate`으로 고객 프로필 + 탐색 기록 + 이번 질문을 결합 (하네스 규칙 2 — 프롬프트 상수화) |
| 파인튜닝·커스터마이징 | 실제 파인튜닝 없이 모델 교체 지점(`OLLAMA_MODEL` 등)을 환경 변수로 노출 (하네스 규칙 4) |
| LLM 프로바이더 추상화 | 인터랙터는 `NclTripPlannerGeneratorPort`만 의존, 구체 LangChain 클래스는 outbound에서만 참조 (하네스 규칙 1) |

### 제안 레이어 구성 (미구현 — 설계 초안)

```text
domain/customer_profile.py                                    # 신규: 선호도·탐색 기록 엔티티
app/dtos/ncl_trip_planner_dto.py
app/ports/input/ncl_trip_planner_use_case.py
app/ports/output/ncl_customer_profile_repository_port.py       # 실시간 고객 프로필 조회
app/ports/output/ncl_trip_planner_generator_port.py            # LangChain 생성 포트
app/use_cases/ncl_trip_planner_interactor.py                   # 프로필 조회 → 체인 호출 → 추천 반환
adapter/outbound/repository/ncl_customer_profile_repository.py
adapter/outbound/client/ncl_trip_planner_generator_client.py   # ChatPromptTemplate + ChatOllama
adapter/inbound/api/schemas/ncl_trip_planner_schema.py
adapter/inbound/api/v1/ncl_trip_planner_router.py              # POST /silicon-valley/ncl/plan
dependencies/ncl_trip_planner_provider.py
```

### 체인 흐름

```text
고객 프로필·탐색 기록 조회 (실시간)
        │
        ▼
ChatPromptTemplate(system: 여행 큐레이터 페르소나 + 프로필/이력 컨텍스트, human: 이번 질문)
        │
        ▼
ChatOllama(model=OLLAMA_MODEL)
        │
        ▼
StrOutputParser → 맞춤형 여행 추천 응답
```

이 설계는 Morningstar 슬라이스와 동일한 패턴을 재사용하므로, 실제 구현은 요청 시 바로
진행할 수 있다.
