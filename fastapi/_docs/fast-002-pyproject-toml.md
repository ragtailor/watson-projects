# A2A 멀티 에이전트 프로젝트 — pyproject.toml 하네스 스펙

## 목적

3개 에이전트(온프레미스 EXAONE, 온프레미스 Qwen, AWS 라우터)로 구성된 A2A-over-MCP 포트폴리오 프로젝트의 파이썬 패키징 구조를 생성한다. 패키지 관리자는 `uv`를 사용한다.

## 아키텍처 전제

- 온프레미스 우분투 서버(RTX 3050 6GB): EXAONE 3.5 2.4B, Qwen2.5 3B를 Ollama로 구동. 그래프 DB(Neo4j) 동거.
- AWS(t4g.micro 또는 Lambda): LLM 없는 오케스트레이터/라우터 에이전트. 온프레미스와 Cloudflare Tunnel/Tailscale 경유 통신.
- 각 에이전트는 MCP 서버로 노출되며, 상대 에이전트를 MCP 클라이언트로 호출한다 (A2A over MCP).
- 그래프 DB는 온프레미스 에이전트만 직접 접근한다. AWS 라우터는 MCP 경유로만 데이터에 접근한다.
- 결과물은 Vercel 프론트엔드로 전달된다 (온프레미스 FastAPI → Vercel fetch).

## 디렉터리 구조 (생성 대상)

```
a2a-mcp/
├── shared/
│   ├── pyproject.toml
│   └── src/
│       └── a2a_shared/
│           ├── __init__.py
│           └── schemas.py          # A2A 메시지 스키마 (pydantic)
├── agents/
│   ├── exaone/
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── agent_exaone/
│   │           └── __init__.py
│   ├── qwen/
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── agent_qwen/
│   │           └── __init__.py
│   └── aws_router/
│       ├── pyproject.toml
│       └── src/
│           └── agent_aws_router/
│               └── __init__.py
└── README.md
```

주의: uv workspace를 사용하지 않는다. 배포 대상이 물리적으로 분리되어 있으므로(우분투 서버 vs AWS), 각 에이전트 디렉터리가 독립적인 `uv sync` 단위가 된다.

## 파일 1: `shared/pyproject.toml`

```toml
[project]
name = "a2a-shared"
version = "0.1.0"
description = "A2A 메시지 스키마 및 공통 타입 (에이전트 간 단일 소스)"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.7",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/a2a_shared"]
```

## 파일 2: `agents/exaone/pyproject.toml`

```toml
[project]
name = "agent-exaone"
version = "0.1.0"
description = "온프레미스 주 추론 에이전트 (EXAONE 3.5 2.4B via Ollama)"
requires-python = ">=3.11"
dependencies = [
    "a2a-shared",
    "fastapi>=0.111",
    "uvicorn[standard]>=0.30",
    "httpx>=0.27",
    "ollama>=0.3",
    "neo4j>=5.20",
    "mcp>=1.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "ruff>=0.5",
    "mypy>=1.10",
]

[tool.uv.sources]
a2a-shared = { path = "../../shared", editable = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/agent_exaone"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
strict = true
```

## 파일 3: `agents/qwen/pyproject.toml`

`agent-exaone`과 동일한 구조. 아래 항목만 다르다.

```toml
[project]
name = "agent-qwen"
version = "0.1.0"
description = "온프레미스 보조 에이전트 (Qwen2.5 3B via Ollama)"
```

나머지 `dependencies`, `dependency-groups`, `tool.uv.sources`, `build-system`, `tool.ruff`, `tool.mypy` 블록은 파일 2와 동일하게 복제하되, `[tool.hatch.build.targets.wheel]`의 packages는 `["src/agent_qwen"]`으로 변경한다.

## 파일 4: `agents/aws_router/pyproject.toml`

LLM·GPU·그래프 DB 의존성을 절대 포함하지 않는다 (`ollama`, `neo4j` 금지). t4g.micro 메모리와 콜드스타트를 위해 최소 의존성을 유지한다.

```toml
[project]
name = "agent-aws-router"
version = "0.1.0"
description = "AWS 오케스트레이터/라우터 에이전트 (LLM 없음, MCP 경유 위임)"
requires-python = ">=3.11"
dependencies = [
    "a2a-shared",
    "fastapi>=0.111",
    "uvicorn[standard]>=0.30",
    "httpx>=0.27",
    "mcp>=1.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "ruff>=0.5",
    "mypy>=1.10",
]

[tool.uv.sources]
a2a-shared = { path = "../../shared", editable = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/agent_aws_router"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
strict = true
```

## 파일 5: `shared/src/a2a_shared/schemas.py` (최소 골격)

```python
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AgentName(StrEnum):
    EXAONE = "exaone"
    QWEN = "qwen"
    AWS_ROUTER = "aws_router"


class A2AMessage(BaseModel):
    """에이전트 간 표준 메시지. 모든 A2A 호출은 이 스키마를 사용한다."""

    sender: AgentName
    receiver: AgentName
    task: str
    payload: dict = Field(default_factory=dict)
    trace_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class A2AResult(BaseModel):
    trace_id: str
    responder: AgentName
    success: bool
    output: dict = Field(default_factory=dict)
    error: str | None = None
```

## 실행 지침 (클로드코드용)

1. 위 디렉터리 구조를 생성한다. 각 `__init__.py`는 빈 파일로 둔다.
2. 파일 1~5를 명시된 경로에 작성한다. 파일 3은 파일 2를 기반으로 지정된 차이점만 반영한다.
3. 각 에이전트 디렉터리에서 `uv sync` 실행이 성공하는지 검증한다:
   ```bash
   cd shared && uv sync && cd ..
   cd agents/exaone && uv sync && cd ../..
   cd agents/qwen && uv sync && cd ../..
   cd agents/aws_router && uv sync && cd ../..
   ```
4. 각 에이전트 환경에서 공통 스키마 import를 검증한다:
   ```bash
   cd agents/exaone && uv run python -c "from a2a_shared.schemas import A2AMessage; print('ok')"
   ```
5. `aws_router` 환경에 `ollama`, `neo4j`가 설치되지 않았음을 확인한다:
   ```bash
   cd agents/aws_router && uv pip list | grep -E "ollama|neo4j" && echo "FAIL: 금지 의존성 발견" || echo "ok"
   ```

## 제약 사항

- 파이썬 버전은 3.11 고정 (`requires-python = ">=3.11"`). 서버와 AWS 인스턴스 간 버전 일치 확인 필요.
- `a2a-shared`는 editable 로컬 경로 의존성이다. 배포 시 각 서버에 `shared/` 디렉터리가 함께 복사되어야 한다 (git clone 단위가 모노레포 전체이므로 충족됨).
- 버전 상한(`<`)은 지정하지 않는다. 잠금은 `uv.lock`이 담당한다.
- 스키마 변경은 반드시 `shared/`에서만 한다. 에이전트 개별 디렉터리에 스키마를 복제하지 않는다.
