# Backend — tailor

FastAPI Python 백엔드. 루트 지침은 [../CLAUDE.md](../CLAUDE.md)를 참고한다.

---

## 실행

```powershell
cd fastapi
$env:PYTHONPATH = ".;apps"
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

---

## 환경 변수

환경 변수 파일은 **전부 `fastapi/` 아래**에 있다 (저장소 루트가 아니다).
`fastapi/.env.example` 하나가 세 파일의 예시를 겸하며, 섹션 표시대로 나눠 담는다.

| 파일 | 읽는 서비스 |
|------|-------------|
| `fastapi/.env` | `api` (공용 설정) |
| `fastapi/.env.backend` | `api` (`JWT_PUBLIC_KEY` 검증 전용) |
| `fastapi/.env.auth` | `auth` (`JWT_PRIVATE_KEY` — 개인키는 여기에만) |

`docker-compose.yml`도 이 디렉터리에 있어 `.env`가 자동 로드된다 (`--env-file` 불필요).

```
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/dbname
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-2.5-flash   # 선택
```

---

## 의존성

```bash
cd fastapi
pip install -r requirements.txt
pip install -r requirements-test.txt
```

---

## DB 마이그레이션

테이블은 앱 시작 시 `create_all_tables()`로 자동 생성된다. Alembic이 필요할 때:

```bash
cd fastapi
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## 아키텍처

**헥사고날(Ports & Adapters)** 아키텍처를 사용한다.

```
fastapi/
├── main.py                 # FastAPI 엔트리포인트, CORS, lifespan
├── core/
│   └── matrix/             # DB 엔진·세션 (SQLAlchemy async), Gemini 클라이언트
└── apps/
    ├── titanic/            # 타이타닉 승객 CSV 업로드·조회 (ML 교육용)
    ├── kingsman/           # 사용자·관리자 관리
    ├── lion_king/          # 소셜 기능 (스켈레톤)
    ├── sherlock_homes/     # 문서 분석
    └── jobs/               # DB 헬스체크
```

각 앱은 다음 레이어로 구성된다.

```
apps/<앱명>/
├── domain/             # 엔티티·값 객체 (순수 비즈니스 로직, 외부 의존 없음)
├── app/
│   ├── ports/input/    # 유스케이스 인터페이스 (입력 포트)
│   ├── ports/output/   # 레포지터리 인터페이스 (출력 포트)
│   ├── dtos/           # Query / Command / Response 데이터 클래스
│   └── use_cases/      # 유스케이스 구현체 (인터랙터)
├── adapter/
│   ├── inbound/api/    # FastAPI 라우터 및 Pydantic 스키마
│   └── outbound/       # ORM 모델, PostgreSQL 레포지터리
├── dependencies/       # FastAPI DI 프로바이더
└── tests/              # 단위 테스트 (TDD, DB 불필요)
    ├── domain/
    ├── app/use_cases/
    └── adapter/
```

**의존성 방향:** `adapter` → `app` → `domain`. 역방향 임포트는 순환 참조를 유발한다.

**Python import 경로:** `fastapi/`와 `fastapi/apps/`가 PYTHONPATH에 포함되므로 `from titanic.xxx import ...` 형태로 임포트한다 (`from apps.titanic.xxx`가 아님).

---

## 앱 목록

| 앱 | 역할 | 토폴로지 | CLAUDE.md |
|----|------|----------|-----------|
| `star_craft` | 온톨로지 인덱스, 컨텍스트 라우팅, 앱 간 오케스트레이션 | **Hub** | — |
| `silicon_valley` | AI 에이전트, 문서 벡터 | Spoke | — |
| `harry_porter` | (미정) | Spoke | — |
| `titanic` | 타이타닉 승객 CSV 업로드·조회 (ML 교육용) | Spoke | [apps/titanic/_docs/CLAUDE.md](apps/titanic/_docs/CLAUDE.md) |
| `kingsman` | 사용자·관리자 관리 | Spoke | — |
| `lion_king` | 소셜 기능 (스켈레톤) | Spoke | — |
| `sherlock_homes` | 문서 분석 | Spoke | — |
| `jobs` | DB 헬스체크 | Spoke | — |

새 앱을 추가할 때 위 표에 행을 추가하고, 토폴로지 역할(Hub/Spoke)을 명시한 뒤 `apps/<앱명>/_docs/CLAUDE.md`를 생성한다.

---

## 네이밍 컨벤션

파일명·클래스명·라우터 prefix에 **영화 캐릭터 이름**을 bounded context 식별자로 사용한다.

예: `james_router`, `rose_router`, `walter_repository`

앱별 캐릭터 목록은 해당 앱의 `_docs/CLAUDE.md`를 참고한다.

---

## 테스트 (TDD)

켄트 벡의 **Red → Green → Refactor** 사이클을 적용한다.

```bash
cd fastapi
python -m pytest                          # 전체
python -m pytest apps/titanic/tests/ -v   # 앱별
```

`pytest.ini`가 `fastapi/` 루트에 있으며 `asyncio_mode = auto`로 설정되어 있다.

---

## 머신러닝 데이터 분석 원칙

### Categorical — 카테고리로 묶이는 데이터

| 척도 | 설명 | 예시 |
|------|------|------|
| **nominal** (명목) | 순서 없이 이름으로만 구분 | 청팀 / 홍팀 / 백팀 |
| **ordinal** (순위) | 순서(서열)가 존재하나 간격은 불균일 | 매우 낮음 / 낮음 / 보통 / 높음 / 매우 높음 |

### Quantitative — 숫자로 측정되는 데이터

| 척도 | 설명 | 예시 |
|------|------|------|
| **interval** (등간) | 일정한 측정 구간, 절대적 원점 없음 — 배율 비교 불가 | 온도, pH, 시간대 |
| **ratio** (비율) | 절대적 원점(0)이 존재 — 배율 비교 가능 | 나이, 금액, 몸무게 |

---

## 스타 토폴로지 아키텍처 (Star Topology)

헥사고날 클린 아키텍처(선형 구조)를 **기반**으로 유지하면서, 앱 간 통신에는 **비선형 스타 토폴로지**를 추가로 적용한다. 두 구조는 중첩된다.

### Hub / Spoke 역할

| 역할 | 앱 | 책임 |
|------|-----|------|
| **Hub** | `star_craft` | 전역 온톨로지 인덱스, 컨텍스트 라우팅, 앱 간 오케스트레이션 |
| Spoke | 그 외 모든 앱 | 독립 도메인 로직; 타 앱과의 통신은 반드시 hub를 경유 |

### 의존성 방향 규칙

```
spoke → hub        ✅ 허용
hub   → spoke      ✅ 허용 (오케스트레이션 목적)
spoke → spoke      ❌ 금지 — 순환 참조·결합도 증가 유발
```

스포크 간 직접 임포트가 필요해 보이는 경우, hub(`star_craft`)에 오케스트레이션 로직을 추가하는 것이 올바른 방법이다.

---

## 하네스 엔지니어링 (Harness Engineering)

안드레이 카파시의 하네스 엔지니어링 철학: **평가·테스트·정적 분석·제약 조건을 촘촘히 배선하여 코드와 데이터의 무결성을 보호한다.**

비선형 스타 토폴로지는 잘못된 연결이 눈에 잘 띄지 않는다. 아래 도구들이 구조 무결성을 자동으로 강제한다.

| 레이어 | 도구 | 설정 파일 | 검증 대상 |
|--------|------|-----------|-----------|
| Python import | `import-linter` | `.importlinter` | spoke → spoke 직접 임포트 금지 |
| MD 온톨로지 노드 | `markdownlint` | `.markdownlint.json` | 메타데이터 구조, 링크 형식 |
| 토폴로지 그래프 | `validate_harness.py` | `scripts/validate_harness.py` | 고립 노드, spoke↔spoke 직접 연결, 순환 참조 |

### 온톨로지 MD 파일 프론트매터 스키마

`_docs/` 하위 모든 MD 파일은 아래 프론트매터를 포함해야 한다.

```yaml
---
type: spoke          # hub 또는 spoke
app: silicon_valley  # 이 문서가 속한 앱 이름
links:               # 연결되는 다른 앱(노드) 목록
  - star_craft
---
```

`type: hub`는 `star_craft` 앱 전용이다. 스포크는 반드시 `star_craft`를 `links`에 포함해야 한다.

### 검증 실행

```bash
cd fastapi

# Python import 의존성 검증
lint-imports

# MD 린트
markdownlint "**/_docs/**/*.md"

# 토폴로지 하네스 검증 (fastapi 루트 기준)
python scripts/validate_harness.py
```

PR 병합 전 세 가지 검증이 모두 통과해야 한다.

---

## async 사용 원칙

메소드에 `async`를 붙일지 여부는 **I/O 여부**로 판단한다.

| 성격 | 형태 | 이유 |
|------|------|------|
| CPU-bound (형태소 분석, 순수 연산 등) | `def` | `async def`로 바꿔도 이벤트 루프를 비블로킹으로 만들지 않음. `async` 표시만 붙고 실제로는 블로킹 — 더 나쁜 상황 |
| I/O-bound (DB, 외부 API, 파일 등) | `async def` | `await`로 이벤트 루프를 양보할 수 있음 |

CPU-bound 작업이 실제로 무거워서 이벤트 루프 블로킹이 문제가 된다면, 메소드를 `async`로 바꾸지 말고 **호출 측에서 스레드풀로 넘긴다.**

```python
await asyncio.to_thread(use_case.analyze_intent, question)
```
