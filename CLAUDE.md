# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 저장소 구조

세 개의 도메인 디렉토리로 이루어진 단일 저장소(모놀리식) 모노레포다.

```
com.ragtailor/
├── fastapi/    # FastAPI Python 백엔드
├── nextjs/     # Next.js TypeScript 프론트엔드
└── flutter/    # Flutter 모바일 앱
```

---

## 하위 CLAUDE.md

작업 영역에 진입하면 해당 문서를 우선 참고한다.

| 영역 | 문서 |
|------|------|
| 백엔드 (fastapi) | [fastapi/CLAUDE.md](fastapi/CLAUDE.md) |
| 프론트엔드 (nextjs) | [nextjs/CLAUDE.md](nextjs/CLAUDE.md) |
| 모바일 (flutter) | [flutter/CLAUDE.md](flutter/CLAUDE.md) |

하위 CLAUDE.md가 루트 지침과 충돌하면 **하위 문서가 우선**한다.

---

## 배포 (odyssey 홈서버)

- 도메인: `api.ragtaylor.com` / 호스트 포트: `8081`
- DB: `ragtaylor_db` (전용 사용자 `ragtaylor_user`) / Redis: DB 번호 `1`
- 공유 인프라(PostgreSQL, Redis)는 별도 저장소 `inception`이 담당하며,
  공유 Docker 네트워크 `dreamscape`를 생성하는 주체다. 이 프로젝트는
  `fastapi/docker-compose.yml`에서 `dreamscape`를 `external: true`로 선언해 합류만 한다.
  네트워크 생성 순서상 `inception`이 먼저 기동되어 있어야 한다.
- n8n, neo4j는 dreamscape와 무관한 이 프로젝트만의 로컬 스택이다.
- compose 프로젝트 이름은 `name: fastapi`로 고정되어 있다. 볼륨·컨테이너 이름의
  접두어가 되므로(`fastapi_n8n_data`, `fastapi_neo4j_data`) 임의로 바꾸면
  기존 데이터가 연결되지 않는다.
- `.env`는 `fastapi/.env`에 둔다 (루트가 아니다). 절대 커밋하지 않으며,
  값 변경 시 `fastapi/.env.example`을 함께 갱신한다.

---

## _docs 위치 규칙

문서 파일(`.md`)은 내용의 범위에 따라 아래 위치에 둔다.

| 범위 | 위치 |
|------|------|
| 공통 (모든 도메인에 걸치는 내용) | `_docs/` |
| 백엔드 전용 | `fastapi/_docs/` |
| 프론트엔드 전용 | `nextjs/_docs/` |
| 모바일 전용 | `flutter/_docs/` |

앱 단위의 세부 문서는 `fastapi/apps/<앱명>/_docs/`에 둔다.

---

## 명령어

도메인마다 스택이 달라 명령어가 공유되지 않는다. 항상 해당 디렉터리로 이동해 실행한다.

**백엔드 (`fastapi/`)** — Python, pip

```bash
cd fastapi
pip install -r requirements.txt
pip install -r requirements-test.txt

PYTHONPATH=".:apps" uvicorn main:app --reload --host 127.0.0.1 --port 8000

python -m pytest                          # 전체 테스트
python -m pytest apps/titanic/tests/ -v   # 앱별 테스트

lint-imports                              # spoke→spoke 임포트 검증
markdownlint "**/_docs/**/*.md"           # 온톨로지 MD 린트
python scripts/validate_harness.py        # 토폴로지 하네스 검증
```

**프론트엔드 (`nextjs/`)** — pnpm 전용. `npm install` / `yarn`은 사용하지 않는다.

```bash
cd nextjs
pnpm dev      # 개발 서버 (localhost:3000)
pnpm build    # 프로덕션 빌드
pnpm lint     # ESLint
```

**모바일 (`flutter/`)**

```bash
cd flutter
flutter pub get
flutter run
flutter test
flutter analyze
```

**인프라 (`fastapi/docker-compose.yml`)** — `nginx`, `certbot`, `n8n`, `pgvector`, `api`,
`auth`, `neo4j` 일곱 서비스를 정의한다. `nextjs`/`flutter`는 Vercel로 배포하므로
nginx/certbot도 `api.ragtaylor.com` / `auth.ragtailor.com`만 담당한다 — 배포 스택 전체가
백엔드 소유라서 compose와 env 파일을 `fastapi/`에 모아 두었다.

```bash
cd fastapi && docker compose up -d
docker compose -f fastapi/docker-compose.yml up -d   # 루트에서 실행해도 동일
docker compose -f fastapi/docker-compose.yml logs -f api
```

프로젝트 디렉터리가 compose 파일 위치로 잡히므로 `fastapi/.env`가 자동 로드된다
(`--env-file` 불필요). nginx 설정·인증서 디렉터리는 저장소 루트에 그대로 두고 `../`로 참조한다.

---

## 환경 변수

`.env`류는 전부 커밋 금지다 (`.gitignore`가 `.env*`, `*.pem`, `*.key`를 차단하며
`.env.example`만 예외). 예시는 **`fastapi/.env.example` 하나로 통합**되어 있으며, 파일 안의
`[.env]` / `[.env.backend]` / `[.env.auth]` 섹션 표시를 보고 해당 파일로 나눠 담는다.
`docker-compose.yml`의 `env_file` 배선은 여전히 세 파일로 분리되어 있다.

**env 파일 3개는 모두 `fastapi/` 아래에 모아 둔다.** 저장소 루트에는 두지 않는다
(`docker-compose.yml`의 `env_file` 경로가 기준).

| 파일 | 예시 출처 | 주요 값 |
|------|-----------|---------|
| `fastapi/.env` | `fastapi/.env.example`의 `[.env]` 섹션 | `DATABASE_URL`, `REDIS_URL`, `CORS_ORIGINS`, `GEMINI_API_KEY`, `NEO4J_*`, `POSTGRES_*`, `AUTH_ID`/`AUTH_PW`/`SESSION_SECRET`, kingsman OAuth 클라이언트 |
| `fastapi/.env.backend` | `fastapi/.env.example`의 `[.env.backend]` 섹션 | `JWT_PUBLIC_KEY`, `SERVICE_AUD` |
| `fastapi/.env.auth` | `fastapi/.env.example`의 `[.env.auth]` 섹션 | `JWT_PRIVATE_KEY`, `JWT_PUBLIC_KEY`, `SERVICE_AUD`, `REDIS_URL` |
| `nextjs/.env.local` | — | `GEMINI_API_KEY`, `NEXT_PUBLIC_API_URL` |

**키 분리 원칙:** RS256 개인키(`JWT_PRIVATE_KEY`)는 `auth` 컨테이너에만 존재한다.
백엔드는 공개키로 검증만 하므로 `fastapi/.env.backend`에 개인키를 넣지 않는다.
예시가 한 파일로 합쳐졌으므로, `fastapi/.env.example`을 통째로 `fastapi/.env`로 복사하면
이 원칙이 깨진다 — `[.env.auth]` 섹션은 반드시 `fastapi/.env.auth`로만 옮긴다.
세 파일이 같은 디렉터리에 모여 있으니 파일명을 혼동하지 않도록 주의한다.

`auth` 쪽 `SERVICE_AUD`와 백엔드 `SERVICE_AUD`가 일치해야 토큰 검증이 통과한다.
OAuth `redirect_uri`는 `{OAUTH_REDIRECT_BASE_URL}/api/kingsman/oauth/{provider}/callback`
형태로 각 프로바이더 콘솔 등록값과 정확히 일치해야 한다.

---

## 테스트

| 도메인 | 프레임워크 | 위치 |
|--------|-----------|------|
| fastapi | pytest (`asyncio_mode = auto`) | `apps/<앱명>/tests/` |
| flutter | `flutter test` | `flutter/test/` |
| nextjs | 없음 | — |

- 백엔드는 **TDD (Red → Green → Refactor)** 를 적용한다. 상세는 [fastapi/CLAUDE.md](fastapi/CLAUDE.md) 참고.
- `fastapi/pytest.ini`의 `testpaths`는 현재 `apps/titanic/tests`, `apps/auth/tests`다.
  새 앱의 테스트를 실행하려면 이 목록에 추가한다.
- `ollama` 마커가 붙은 테스트는 Ollama 서버가 필요하며 `addopts = -m "not ollama"`로 기본 제외된다.
  실행하려면 `python -m pytest -m ollama`.
- 단위 테스트는 DB 없이 돌아야 한다 (`domain` / `app/use_cases` 레이어).
- nextjs에는 테스트 하네스가 없다. 변경 검증은 `pnpm build`로 한다.

---

## 코딩 컨벤션 (공통)

도메인별 상세 규칙은 하위 CLAUDE.md와 `.claude/rules/`에 있다.
`.claude/rules/`의 파일은 `paths` 프론트매터로 적용 대상 파일이 정해진다
(예: `typescript.md` → `**/*.ts`, `**/*.tsx`).

- 문서·주석·커밋 메시지·사용자에게 노출되는 에러 메시지는 **한국어**로 쓴다.
- 커밋 메시지는 **Conventional Commits** 형식을 쓴다 (`feat:` / `fix:` / `docs:` / `refactor:` / `chore:`).
  - 제목은 50자 이내로, 한국어로 쓴다.
  - 예: `feat: 사용자 로그인 기능 추가`
- 도메인 디렉터리(`fastapi` / `nextjs` / `flutter`) 간에는 코드를 직접 임포트하지 않는다.
  통신은 HTTP API로만 한다.
- 비밀값은 코드에 하드코딩하지 않고 환경 변수로 주입한다.

---

## 브랜치 전략

- `main`: 유일한 통합 브랜치. 현재 작업은 main에 직접 커밋한다.
- `desktop`: 작업 PC 동기화용 보조 브랜치.
- 별도 develop / feature 브랜치 흐름은 현재 운용하지 않는다.

---

## 주의사항

- **비밀값 커밋 금지** — `.env*`(예시 파일 제외), `*.pem`, `*.key`, 특히 `jwt_private.pem`.
- **`fastapi`: spoke → spoke 직접 임포트 금지.** 앱 간 통신은 hub(`star_craft`)를 경유한다.
  `lint-imports`가 이를 강제한다.
- **`fastapi` 임포트 경로** — `fastapi/`와 `fastapi/apps/`가 PYTHONPATH에 들어가므로
  `from titanic.xxx import ...` 형태로 쓴다 (`from apps.titanic.xxx`가 아님).
- **`nextjs/components/ui/`는 shadcn/ui 자동 생성물이다.** 직접 수정하지 않고
  `pnpm dlx shadcn@latest add <component>`로 갱신한다.
- **`nextjs/next.config.mjs`의 `typescript.ignoreBuildErrors: true`는 의도된 설정이다.**
  단, 타입 에러를 방치해도 된다는 뜻은 아니다.
- **`flutter/CLAUDE.md`는 현재 비어 있다.** 모바일 작업 전 내용을 채운다.
- 컨테이너 기동은 `inception`이 먼저 올라와 있어야 한다 (공유 네트워크 `dreamscape` 생성 주체).

---

# LLM 코딩 행동 지침

일반적인 LLM 코딩 실수를 줄이기 위한 행동 지침이다. [Andrej Karpathy의 관찰](https://x.com/karpathy/status/2015883857489522876)을 바탕으로 정리되었다. 프로젝트별 지침이 있으면 본 문서와 병합하여 사용한다.

**트레이드오프:** 속도보다 신중함에 우선한다. 사소한 작업은 상황에 맞게 판단한다.

---

## 1. Think Before Coding (구현 전 사고)

**가정하지 않는다. 혼란을 숨기지 않는다. 트레이드오프를 드러낸다.**

구현에 들어가기 전에 다음을 지킨다.

- 가정은 명시한다. 불확실하면 질문한다.
- 해석이 여러 가지면 조용히 하나를 고르지 말고, 가능한 해석을 모두 제시한다.
- 더 단순한 방법이 있으면 말한다. 타당하면 사용자 요청에 반대·수정 의견을 낸다.
- 불명확하면 멈춘다. 무엇이 혼란스러운지 이름 붙이고 질문한다.

---

## 2. Simplicity First (단순성 우선)

**문제를 푸는 데 필요한 최소한의 코드만 쓴다. 추측성 내용은 넣지 않는다.**

- 요청받지 않은 기능은 넣지 않는다.
- 일회성 코드를 위한 추상화는 만들지 않는다.
- 요청받지 않은 "유연함"이나 "설정 가능성"은 넣지 않는다.
- 현실적으로 일어날 수 없는 시나리오를 위한 예외 처리는 하지 않는다.
- 200줄로 쓸 수 있는 것을 50줄로 줄일 수 있으면 다시 쓴다.

스스로에게 묻는다: "시니어 엔지니어가 이건 과하게 복잡하다고 할까?" 그렇다면 단순화한다.

---

## 3. Surgical Changes (정밀한 수정)

**꼭 필요한 곳만 손대고, 본인이 만든 잔여만 정리한다.**

기존 코드를 고칠 때:

- 인접한 코드·주석·포맷을 "개선"하지 않는다.
- 망가지지 않은 부분은 리팩터링하지 않는다.
- 본인 스타일과 달라도 기존 스타일을 맞춘다.
- 작업과 무관한 데드 코드를 발견하면 언급만 하고, 임의로 삭제하지 않는다.

본인 변경으로 쓰이지 않게 된 것이 있으면:

- 본인 변경 때문에 불필요해진 import·변수·함수는 제거한다.
- 원래부터 있던 데드 코드는 요청이 없으면 제거하지 않는다.

**검증:** 바뀐 모든 줄이 사용자 요청과 직접적으로 연결되어야 한다.

---

## 4. Goal-Driven Execution (목표 중심 실행)

**성공 기준을 정의한다. 검증될 때까지 반복한다.**

작업을 검증 가능한 목표로 바꾼다.

- "유효성 검사 추가" → "잘못된 입력에 대한 테스트를 쓰고, 통과시킨다"
- "버그 수정" → "재현 테스트를 쓰고, 통과시킨다"
- "X 리팩터링" → "전후로 테스트가 통과함을 확인한다"

다단계 작업이면 짧은 계획을 쓴다.

```text
1. [단계] → 검증: [확인 사항]
2. [단계] → 검증: [확인 사항]
3. [단계] → 검증: [확인 사항]
```

성공 기준이 분명해야 같은 기준으로 반복할 수 있다. "작동만 하게"처럼 약한 기준은 계속 되묻게 만든다.
