# a2a-mcp

A2A-over-MCP 멀티 에이전트 포트폴리오 프로젝트. 3개의 독립적인 에이전트로 구성된다.

- `agents/exaone` — 온프레미스 주 추론 에이전트 (EXAONE 3.5 2.4B via Ollama)
- `agents/qwen` — 온프레미스 보조 에이전트 (Qwen2.5 3B via Ollama)
- `agents/aws_router` — AWS 오케스트레이터/라우터 에이전트 (LLM 없음, MCP 경유 위임)
- `shared` — 에이전트 간 공통 A2A 메시지 스키마 (`a2a-shared`)

각 에이전트는 배포 대상이 물리적으로 분리되어 있으므로(온프레미스 우분투 서버 vs AWS)
uv workspace를 사용하지 않고, 각 디렉터리가 독립적인 `uv sync` 단위로 동작한다.

상세 스펙: [fastapi/_docs/fast-002-pyproject-toml.md](../fastapi/_docs/fast-002-pyproject-toml.md)

## 설치

```bash
cd shared && uv sync && cd ..
cd agents/exaone && uv sync && cd ../..
cd agents/qwen && uv sync && cd ../..
cd agents/aws_router && uv sync && cd ../..
```
