---
type: spoke
app: silicon_valley
links:
  - star_craft
---

# LangChain 작업 하네스

Claude가 이 저장소에서 LangChain 관련 작업을 할 때 지켜야 할 규칙이다.
LangChain의 강점/약점을 이 프로젝트의 헥사고날 구조에 맞춘 실행 가능한 체크리스트로 변환한 것이며,
막연한 소개가 아니라 **작업 전/작업 중/작업 완료 전에 실제로 확인해야 하는 항목**이다.

---

## 0. 컨텍스트

- 이 저장소에서 LangChain은 현재 `silicon_valley` 앱의 Morningstar 인사이트 엔진에서 사용 중이다.
  ([005-langchain-morningstar-strategy.md](005-langchain-morningstar-strategy.md) 참고)
- 설치된 패키지: `langchain`, `langchain-community`, `langsmith`, `langgraph`. 별도 provider 패키지
  (`langchain-google-genai` 등)는 없으며, 로컬 Ollama(`core/lol/t1_mid_faker_orchestrator.py`와 동일한
  관례, `ChatOllama`)가 기본 LLM 경로다.
- 헥사고날 구조상 LLM 호출은 항상 `app/ports/output/*_port.py` 뒤에 둔다. LangChain의 구체 클래스는
  `adapter/outbound/client/*`에서만 임포트한다.

---

## 1. 절대 규칙 (LangChain의 강점을 실제로 살리기 위한 규칙)

1. **LLM 프로바이더는 포트 뒤에 숨긴다.** 인터랙터·도메인 코드가 `ChatOllama`,
   `ChatGoogleGenerativeAI` 같은 LangChain 통합 클래스를 직접 참조하지 않는다. "다양한 LLM을
   내 마음대로 통합"하는 강점은 실제로 교체 가능할 때만 의미가 있다.
2. **프롬프트는 `ChatPromptTemplate`/`PromptTemplate`로 모듈 상단에 상수 선언한다.** 함수 본문에
   f-string을 흩뿌리지 않는다. 유연한 프롬프팅·컨텍스트 관리 기능은 프롬프트가 한곳에 모여 있을
   때만 유지보수 가능하다.
3. **실시간/외부 데이터 소스(DB, API, 파일)는 매 요청마다 output port(repository/client)로
   조회한다.** 요청 시점 이전에 캐시된 값을 재사용하지 않는다. "데이터 반응형 애플리케이션" 강점은
   조회 시점이 곧 응답 시점일 때만 성립한다.
4. **모델 교체 지점(모델명, base_url 등)은 환경 변수로 노출한다.** 코드에 하드코딩하지 않는다.
   이 프로젝트에는 실제 파인튜닝 인프라가 없으므로, "파인튜닝·커스터마이징" 강점은 모델을 손쉽게
   갈아 끼우는 것으로 대체한다.

---

## 2. 체크리스트 (LangChain의 약점을 미리 걸러내기 위한 확인 사항)

작업을 완료로 보고하기 전에 아래를 확인한다.

- [ ] **성능:** 체인이 실제로 여러 단계(검색 → 프롬프팅 → 생성 등)를 필요로 하는가? 단일 LLM
      호출로 충분하다면 LangChain 체인 대신 기존 `httpx` 직접 호출(`piper_gilfoyle_llm_client.py`
      패턴)을 쓴다. 불필요한 체인은 성능 저하와 복잡도만 늘린다.
- [ ] **러닝 커브:** 새 체인/에이전트 구조를 도입하기 전에, 이미 있는
      `prompt | llm | StrOutputParser()` LCEL 패턴(`morningstar_insight_generator_client.py`)으로
      표현 가능한지 먼저 확인한다. Agents·Tools·Memory 같은 낯선 추상화는 실제로 필요할 때만
      도입한다.
- [ ] **적합성:** 이 유즈케이스가 LangChain 없이(순수 API 호출 또는 직접 프롬프트 문자열)로 더
      단순하게 풀리지는 않는지 재검토한다. 모든 유즈케이스에 LangChain이 최적은 아니다.

---

## 3. 참고

- 실제 적용 예: [005-langchain-morningstar-strategy.md](005-langchain-morningstar-strategy.md)
