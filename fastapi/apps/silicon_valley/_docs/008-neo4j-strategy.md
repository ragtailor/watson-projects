---
type: spoke
app: silicon_valley
links:
  - star_craft
---

# Neo4j 전략 — Docker 설치 및 연결

[004-langgraph-harness.md](004-langgraph-harness.md)의 체크리스트("Neo4j 실 연결이 아직 없는 상태라면,
002 harness의 노드/라벨/관계/속성 모델을 먼저 확정한 뒤 드라이버·포트를 연결했는가?")가 지적한
격차를 메우는 문서다. LangGraph 추론 노드가 실제로 그래프를 조회하려면, 그 전에 Neo4j 컨테이너가
기동되고 앱 코드가 실제로 접속할 수 있어야 한다. 이 문서는 **컨테이너 설치와 연결**까지만 다루고,
GraphRAG 추론 로직 자체는 004번 문서의 "예상 구현 매핑"을 따른다.

---

## 0. 현재 상태

### 이미 있는 것

| 항목 | 위치 |
| ---- | ---- |
| `neo4j` 서비스 (image `neo4j:5`, 포트 `7474`/`7687`, `NEO4J_AUTH`, 볼륨 `neo4j_data`) | `docker-compose.yml` (커밋 `52d4fc9`) |
| `api` 서비스의 `depends_on: neo4j` | `docker-compose.yml` |
| `NEO4J_PASSWORD` | `.env.example` |
| `neo4j-graphrag` 패키지 | `fastapi/requirements.txt` — 단, 현재는 PDF 텍스트 추출(`PdfLoader`)에만 쓰이고 실제 그래프 조회에는 안 쓰인다 |

`neo4j` 서비스에 `networks:`가 지정돼 있지 않아 기본(default) 네트워크에만 속한다. 이는 루트
CLAUDE.md의 배포 규칙("n8n, neo4j는 dreamscape와 무관한 이 프로젝트만의 로컬 스택")과 이미
일치하므로 **변경하지 않는다**.

### 아직 없는 것

- `NEO4J_URI`, `NEO4J_USER` 환경 변수 — 지금은 비밀번호만 있고 접속 주소·계정이 없다.
- `neo4j` 서비스의 healthcheck — `depends_on: neo4j`만으로는 컨테이너가 "떴다"만 보장하지
  "쿼리를 받을 준비가 됐다"는 보장하지 않는다.
- Python에서 실제로 드라이버를 여는 코드 — `core/matrix`에 Postgres(`grid_oracle_database_manager.py`),
  Redis(`totem_redis_cache_manager.py`)에 대응하는 Neo4j 연결 관리자가 없다.
- 출력 포트/어댑터 — [star-001-pipeline.md](../../star_craft/_docs/star-001-pipeline.md)에 설계만
  있고 실제 파일(`graph_repository_port.py` 등)은 없다.
- `requirements.txt`에 `neo4j` 드라이버가 명시돼 있지 않다 (`neo4j-graphrag`가 내부적으로 의존하고
  있을 가능성이 높지만, 버전을 직접 고정하지 않으면 `neo4j-graphrag` 업데이트에 따라 암묵적으로
  바뀔 수 있다).

---

## 1. 설계 결정 — 같은 컨테이너, 라벨로 분리

Neo4j를 쓰려는 목적이 이미 두 갈래로 갈라져 있다.

| 용도 | 문서 | 데이터 성격 |
| ---- | ---- | ---- |
| 허브 온톨로지 인덱스 (앱 노드·관계) | [star-001-pipeline.md](../../star_craft/_docs/star-001-pipeline.md) | `Hub`/`Spoke` 라벨, 앱 간 연결 |
| GraphRAG 지식 그래프 (문서 엔티티·관계) | [004-langgraph-harness.md](004-langgraph-harness.md) | 문서에서 추출한 엔티티/개념 라벨 |

`docker-compose.yml`의 `neo4j:5` 이미지는 커뮤니티 에디션이라 **멀티 데이터베이스(`CREATE DATABASE`)를
지원하지 않는다** (엔터프라이즈 전용 기능). 별도 컨테이너를 새로 띄우는 대신, **같은 컨테이너·같은
기본 데이터베이스를 공유하되 라벨을 네임스페이스로 분리**한다.

- 허브 온톨로지: `Hub`, `Spoke` (star-001 스키마 그대로)
- GraphRAG 지식 그래프: `Document`, `Entity` 등 문서 도메인 전용 라벨 (제네릭한 `Person`/`Book`
  예시는 [002-neo4j-harness.md](002-neo4j-harness.md) 참고, 실제 라벨은 구현 시 확정)

Cypher 쿼리를 짤 때 항상 라벨로 범위를 좁혀서 두 그래프가 서로 섞이지 않게 한다. 컨테이너·자격
증명·드라이버 연결 관리자는 하나만 있으면 된다.

---

## 2. Docker 설치 전략

### 2.1 healthcheck 추가

```yaml
  neo4j:
    image: neo4j:5
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
    volumes:
      - neo4j_data:/data
    healthcheck:
      test: ["CMD-SHELL", "cypher-shell -u neo4j -p \"$$NEO4J_PASSWORD\" 'RETURN 1' || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s
```

`api` 서비스의 `depends_on`을 조건부로 강화한다.

```yaml
  api:
    depends_on:
      neo4j:
        condition: service_healthy
```

### 2.2 접속 정보 환경 변수

`.env.example`에 추가:

```text
NEO4J_URI=bolt://neo4j:7687   # 도커 네트워크 내부에서는 서비스명으로 접속
NEO4J_USER=neo4j
# NEO4J_PASSWORD는 이미 있음
```

로컬에서 `fastapi/CLAUDE.md`의 실행법(`uvicorn --reload`, 컨테이너 밖)으로 개발할 때는 `neo4j`
서비스만 `docker compose up -d neo4j`로 띄워둔 채 `.env`에서 `NEO4J_URI=bolt://localhost:7687`로
덮어써서 접속한다 (포트가 호스트에 이미 퍼블리시돼 있으므로 별도 설정 불필요).

### 2.3 core/matrix 연결 관리자 (신규 — 설계 초안, 미구현)

Postgres(`grid_oracle_database_manager.py`)·Redis(`totem_redis_cache_manager.py`)와 동일한
init/get/dispose 패턴을 따른다. Matrix 세계관 중 그래프 구조 전체를 설계하는 인물인
"Architect"에서 따와 `core/matrix/grid_architect_graph_manager.py`로 제안한다.

```python
from __future__ import annotations

import os

from neo4j import AsyncDriver, AsyncGraphDatabase

_driver: AsyncDriver | None = None


def init_driver() -> None:
    global _driver
    if _driver is not None:
        return

    uri = os.getenv("NEO4J_URI")
    if not uri:
        return

    _driver = AsyncGraphDatabase.driver(
        uri,
        auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD")),
    )


def get_driver() -> AsyncDriver:
    if _driver is None:
        init_driver()

    if _driver is None:
        raise RuntimeError("NEO4J_URI가 설정되지 않아 Neo4j 드라이버를 초기화할 수 없습니다.")

    return _driver


async def dispose_driver() -> None:
    global _driver
    if _driver is not None:
        await _driver.close()
    _driver = None
```

`main.py`의 `lifespan`에 Postgres 엔진과 동일하게 `init_driver()`/`dispose_driver()`를 연결한다.

### 2.4 헥사고날 포트/어댑터

- `star_craft` 허브 온톨로지 쪽: star-001에서 이미 설계한
  `app/ports/output/graph_repository_port.py` + `adapter/outbound/neo4j_graph_repository.py`를
  그대로 따른다.
- `silicon_valley` GraphRAG 쪽: 004번 문서의 "예상 구현 매핑"에 있는
  `app/ports/output/graph_reasoning_port.py` + `adapter/outbound/client/graph_reasoning_client.py`가
  내부적으로 `grid_architect_graph_manager.get_driver()`를 사용해 세션을 연다. LangGraph 노드
  함수는 이 포트만 의존한다 (004 하네스 규칙 5).

### 2.5 requirements.txt

```text
neo4j>=5.0,<6.0   # neo4j-graphrag가 암묵적으로 의존하는 드라이버를 명시적으로 고정
```

---

## 3. 검증 절차

1. `docker compose up -d neo4j` → `docker compose ps`로 `healthy` 상태 확인
2. `http://localhost:7474`(Neo4j Browser)에서 `NEO4J_AUTH` 계정으로 로그인 확인
3. `cypher-shell -a bolt://localhost:7687 -u neo4j -p $NEO4J_PASSWORD "RETURN 1"`로 드라이버 레벨
   접속 확인
4. `grid_architect_graph_manager` 작성 후, FastAPI 기동 로그에서 초기화 실패 없이 뜨는지 확인
   (`NEO4J_URI` 미설정 시에도 앱 전체가 죽지 않고 해당 기능만 비활성화되는지 — Redis 매니저와
   동일한 방어적 패턴)
5. `cd fastapi && lint-imports` — 신규 포트/어댑터가 spoke → spoke 규칙을 위반하지 않는지 재확인

---

## 4. 구현 순서

```text
1. docker-compose.yml에 healthcheck 추가                    → 검증: docker compose ps에서 healthy
2. .env / .env.example에 NEO4J_URI, NEO4J_USER 추가          → 검증: 컨테이너 안 env 값 로드 확인
3. requirements.txt에 neo4j 드라이버 명시적 추가              → 검증: pip install 성공
4. core/matrix/grid_architect_graph_manager.py 작성          → 검증: init/get/dispose 단위 테스트
5. main.py lifespan에 init_driver/dispose_driver 연결        → 검증: 앱 기동·종료 로그
6. star_craft·silicon_valley 각각의 출력 포트/어댑터 작성      → 검증: 004/star-001 체크리스트 재확인
```

---

## 5. 참고

- [004-langgraph-harness.md](004-langgraph-harness.md)
- [002-neo4j-harness.md](002-neo4j-harness.md)
- [../../star_craft/_docs/star-001-pipeline.md](../../star_craft/_docs/star-001-pipeline.md)
