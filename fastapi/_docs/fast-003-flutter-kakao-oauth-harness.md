---
type: spoke
app: auth
links:
  - star_craft
---

# FAST-003 — 카카오 OIDC 로그인 + 모바일/웹 분리 인증 게이트웨이 (백엔드)

`auth` 컨테이너(`auth.ragtailor.com`)에 **카카오 OIDC `id_token` 검증 로그인**을 추가하고,
**모바일/웹 세션을 완전히 분리**하는 작업의 하네스 스펙이다.

- 기준일: 2026-08-03
- 대상: `fastapi/auth_main.py` + `fastapi/apps/auth/`, `fastapi/core/security.py`
- 짝 문서(클라이언트): [`flutter/_docs/flutter-kakao-oauth-harness.md`](../../flutter/_docs/flutter-kakao-oauth-harness.md)
- **이 문서는 스펙이며 구현 코드를 포함하지 않는다.** 각 단계의 "검증"으로 완료를 판정한다.

> **구현 상태 (2026-08-03)**: §9의 결정 5건이 확정되어 §5 전 단계가 구현됐다.
> 신규 파일 — `apps/auth/oidc/kakao_verifier.py`, `apps/auth/store/refresh_store.py`,
> `apps/auth/identity.py`. 테스트 — `apps/auth/tests/test_kakao_verifier.py`,
> `test_platform_sessions.py`, `test_refresh_rotation.py`(플랫폼 API로 갱신).

---

## 0. 역할

`ragtailor` 인증 게이트웨이를 구현하는 백엔드 엔지니어 관점의 작업 지시서다.
아래 §5 작업 순서를 단계별로 진행하고, 각 단계마다 **변경 파일과 이유**를 요약한 뒤 다음으로 넘어간다.
불명확한 지점은 임의로 확장하지 말고 §9의 "결정 필요"에 올린 뒤 가정을 명시하고 진행한다.

---

## 1. 저장소 현황 — 이미 있는 것

원본 스펙은 "새로 만든다"를 전제하지만, 저장소에는 인증 게이트웨이가 **이미 동작 중**이다.
아래를 먼저 읽지 않고 새 모듈을 만들면 중복 구현이 된다.

| 위치 | 현재 하는 일 |
|------|--------------|
| `fastapi/auth_main.py` | `auth` 전용 엔트리포인트. `/auth` prefix로 라우터 include, `/healthz` |
| `apps/auth/router.py` | `POST /auth/login`(인가 코드), `/auth/logout`, `/auth/refresh`, `GET /auth/callback/{provider}`, `GET /auth/.well-known/jwks.json` |
| `apps/auth/services.py` | 리프레시 로테이션 + **재사용 감지 시 세션 패밀리 전체 폐기**. Redis 키 `auth:refresh:{jti}`(String), `auth:refresh:family:{sub}`(SET), TTL 14일 |
| `apps/auth/schemas.py` | `LoginRequest(provider, code)`, `RefreshRequest`, `TokenResponse` |
| `apps/auth/rbac.py` | `Role`, `Permission`, `Provider`(google/**kakao**/naver/x) |
| `core/security.py` | RS256 발급·검증, JWKS(`kid` = RFC 7638 thumbprint), `ACCESS_TOKEN_DEFAULT_MIN=10`, `REFRESH_TOKEN_TTL_DAYS=14`, 쿠키 속성 |
| `core/matrix/totem_redis_cache_manager.py` | `REDIS_URL`로 만드는 `redis.asyncio` 클라이언트(`decode_responses=True`) |
| `apps/kingsman/.../kakao_oauth_adapter.py` | **웹 인가코드 플로우** — `kauth.kakao.com/oauth/token` + KAPI `/v2/user/me` |
| `apps/kingsman/.../orm/user_orm.py` | `kingsman_users` 테이블. `UNIQUE(oauth_provider, oauth_subject)` |
| `apps/auth/tests/` | `test_security.py`, `test_refresh_rotation.py` (monkeypatch 기반 fake redis) |

즉 이번 작업은 **신규 구축이 아니라 확장**이다. `POST /auth/kakao/login`을 추가하고,
기존 발급·로테이션 경로에 `platform` 축을 관철시키는 일이다.

---

## 2. 원본 스펙과 저장소의 차이 — 착수 전 확정 사항

원본 프롬프트를 그대로 실행하면 저장소와 충돌하는 지점이 다섯 군데 있다. 아래로 대체한다.

### 2.1 `.env.auth`는 폐지됐다

- 스펙: "`.env.auth`에서 로드"
- 실제: env 파일은 **`fastapi/.env` 하나**이며 `api`/`auth`가 공유한다. 예시는 `fastapi/.env.example`.
- **→ 새 키는 전부 `fastapi/.env`에 넣고 `fastapi/.env.example`을 같은 커밋에서 갱신한다.**
  같은 키를 파일 안에 두 번 정의하지 않는다(마지막 값이 조용히 이긴다).

### 2.2 `JWT_PRIVATE_KEY_PATH` / `JWT_PUBLIC_KEY_PATH`는 없다

- 실제: `JWT_PRIVATE_KEY` / `JWT_PUBLIC_KEY`에 **PEM 원문 또는 base64**를 넣는다(`core.config`가 해석).
- **→ 경로 기반 키 로딩을 새로 만들지 않는다.** 기존 `core.config` 접근자를 그대로 쓴다.

### 2.3 Redis 키 네임스페이스가 겹친다 (가장 중요)

- 스펙: `auth:refresh:{user_id}` (Hash)
- 실제: `auth:refresh:{jti}` (String), `auth:refresh:family:{sub}` (SET)
- 같은 `auth:refresh:` 접두어 아래 String·SET·Hash가 섞이면 운영 중 키를 스캔·삭제할 때
  타입을 구분할 수 없고, 잘못된 타입 명령은 `WRONGTYPE`으로 죽는다.
- **→ 플랫폼 슬롯은 별도 네임스페이스 `auth:session:{sub}` (Hash)로 만든다.**
  스펙의 의도("유저 1인당 Hash + 플랫폼별 필드")는 그대로 지키고 접두어만 분리한다.

### 2.4 발급 토큰에 `platform` 클레임이 없다

- 실제: `create_access_token(sub, roles, aud)` / `create_refresh_token(sub)` — 플랫폼 개념 없음.
  TTL도 모듈 상수(`ACCESS_TOKEN_DEFAULT_MIN`, `REFRESH_TOKEN_TTL_DAYS`)로 고정.
- **→ `core/security.py`에 `platform`을 추가한다.** `core`는 `api` 컨테이너도 쓰므로,
  변경은 **발급부에 인자 추가 + 검증부에 클레임 노출**까지만 하고 검증 정책은 `auth` 쪽에 둔다.
- 배포 시점의 기존 세션에는 `platform`이 없다. **누락 토큰은 거부**한다(전원 1회 재로그인).
  "없으면 web으로 간주"는 교차 오염 방지 요건을 무너뜨리므로 채택하지 않는다.

### 2.5 현행 `logout`은 세션 **전체**를 폐기한다

- 실제: `services.logout()` → `_revoke_family(sub)` → 그 유저의 모든 리프레시 폐기.
- 스펙 요건: 모바일 로그아웃 시 웹 세션 생존.
- **→ `logout`은 요청 `platform` 슬롯만 지운다.** 전체 폐기는 재사용 감지(침해 의심) 경로에만 남긴다.
  이 둘을 같은 함수로 합치지 않는다.

---

## 3. 아키텍처 결정

### 3.1 OIDC `id_token` 검증 흐름

```text
[Flutter/Web] 카카오 SDK 로그인 → id_token 획득
      │  Authorization 헤더 없음. body = { id_token, platform, nonce }
      ▼
[auth] POST /auth/kakao/login
   1) openid-configuration에서 issuer / jwks_uri 확보      (캐시)
   2) id_token 헤더의 kid로 JWKS 공개키 매칭               (캐시, miss 시에만 갱신)
   3) RS256 서명 검증
   4) 클레임 검증: iss / aud / exp / nonce
   5) sub, email, nickname 추출
   6) DB 조회 → 없으면 가입, 있으면 로그인
   7) 자체 JWT(access/refresh) 발급 — platform 클레임 포함
   8) refresh를 Redis 플랫폼 슬롯에 저장(해시 + 메타)
      ▼
[Client] access + refresh 수신
```

- 기본 경로에서 **KAPI(`/v2/user/me`) 호출 없음.** 상세 프로필이 필요해지면 별도 엔드포인트에서
  카카오 access token으로 조회하도록 확장 지점만 남긴다(이번 범위 밖).
- 카카오 OIDC 엔드포인트(구현 시 카카오 개발자 문서로 재확인):
  - discovery: `https://kauth.kakao.com/.well-known/openid-configuration`
  - issuer: `https://kauth.kakao.com`
  - jwks: `https://kauth.kakao.com/.well-known/jwks.json`
- `aud`는 **카카오 앱의 REST API 키**다. 네이티브 앱 키가 아니다.
  `.env`의 `KAKAO_CLIENT_ID`(kingsman이 이미 쓰는 값)와 같은 앱이면 그대로 재사용하고,
  모바일용 카카오 앱을 따로 팠다면 **허용 aud 목록**이 필요하다 → §9 결정 필요.
- `nonce`: 클라이언트가 생성해 카카오 로그인에 넣고, 같은 값을 body로 보낸다.
  서버는 `id_token.nonce`와 body의 `nonce`를 비교한다. 재생 공격 차단이 목적이므로
  **`nonce` 누락은 허용하지 않는다**(스펙의 `nonce: str | None`을 필수로 좁힌다).

### 3.2 모바일 / 웹 완전 분리

| 항목 | 규칙 |
|------|------|
| 요청 | `platform: Literal["mobile","web"]` **필수**. 누락·오타 → 400 |
| 토큰 | access/refresh **양쪽 payload에 `platform` 클레임** |
| TTL | 플랫폼별 독립 설정 (env) |
| refresh | 요청 `platform` ≠ 토큰 `platform` 클레임 → **401**. Redis 대조도 해당 슬롯만 |
| logout | 해당 `platform` 슬롯만 삭제 |
| 전달 방식 | web = 쿠키(기존 `COOKIE_KWARGS` 유지), mobile = **응답 body**(쿠키 미설정) |

모바일에 쿠키를 세팅하지 않는 이유: `COOKIE_KWARGS`의 `domain=".ragtailor.com"` /
`secure` / `samesite=lax`는 브라우저 전제이고, 앱은 쿠키 저장소가 아니라 보안 저장소를 쓴다.
`platform="mobile"`이면 `Set-Cookie`를 붙이지 않는다.

TTL 기본값(값은 자유, config로 분리):

| 플랫폼 | access | refresh |
|--------|--------|---------|
| web | 30m | 7d |
| mobile | 60m | 30d |

> 현행 상수는 access 10m / refresh 14d다. 위 값으로 바꾸면 **기존 `/auth/login` 경로의 수명도 바뀐다.**
> 상수를 지우지 말고 플랫폼 값이 없을 때의 기본값으로 남긴다.

### 3.3 Redis 저장 구조

"모바일 토큰 컬럼 추가"를 **유저 1인당 Hash 1개 + 플랫폼별 필드**로 구현한다.
(§2.3에 따라 접두어는 `auth:session:`)

```text
auth:session:{sub}   (Hash)
  ├─ web    : {"th":"<sha256>","jti":"...","iat":...,"exp":...}
  └─ mobile : {"th":"<sha256>","jti":"...","iat":...,"exp":...}   ← 이번에 추가되는 슬롯
```

- 값은 **리프레시 원문이 아니라 SHA-256 해시 + 메타(jti, iat, exp)** JSON.
- 필드 단위 TTL이 없으므로 만료 판정은 값 안의 `exp`로 **애플리케이션이** 한다.
  Hash 자체에는 가장 긴 플랫폼 TTL을 `EXPIRE`로 보조 설정한다(고아 키 청소용).
- `logout(mobile)` = `HDEL auth:session:{sub} mobile` → web 슬롯 생존.
- 로테이션: 검증 통과 시 같은 필드를 **새 값으로 덮어쓴다**. 저장된 `th`와 불일치하는
  (서명·만료는 유효한) 리프레시가 오면 **재사용**으로 판정한다.
- 재사용 감지 시 폐기 범위: **해당 플랫폼 슬롯만** 지운다.
  전체 폐기는 웹 세션까지 끊어 교차 오염 금지 원칙을 스스로 어긴다 → §9 결정 필요.

**트레이드오프(반드시 인지):** 플랫폼당 슬롯이 1개이므로 **같은 플랫폼 기기 2대 동시 로그인은
나중 로그인이 앞 기기를 밀어낸다.** 폰+태블릿 동시 사용을 지원하려면 슬롯을
`{platform}:{device_id}` 필드로 넓혀야 한다. 이번 범위에서는 1슬롯으로 간다.

### 3.4 JWKS / OIDC 설정 캐싱

- discovery·JWKS는 매 요청 조회 금지. **인메모리 캐시 + TTL 6h.**
- `kid` miss일 때만 강제 리프레시(키 롤오버 대응). 갱신 후에도 miss면 401(토큰 쪽 문제).
- 외부 호출 실패 시 캐시로 폴백, 캐시조차 없으면 **503**으로 명확히 실패시킨다(401로 뭉개지 않는다).
- `auth` 컨테이너는 워커가 여러 개일 수 있다. 캐시는 워커 로컬이며 그래도 무방하다
  (워커당 6h에 1회 조회). Redis 공유 캐시는 만들지 않는다 — 불필요한 복잡도다.

---

## 4. 제약

- 클라이언트가 보낸 프로필(email, nickname)은 **절대 신뢰하지 않는다.** 검증된 `id_token` 클레임만 쓴다.
- 서명 검증 없이 payload만 디코드해 사용하는 코드 금지.
  (예외: `services._issue_pair`처럼 **방금 자기가 만든** 토큰에서 `jti`만 읽는 경우 — 기존 주석 참고)
- 검증 허용 알고리즘은 `["RS256"]` 리터럴 하드코딩 유지. 설정으로 빼지 않는다.
- 개인키를 읽는 코드는 발급부에만 존재한다. `main.py`(api) 경로에 발급 코드를 추가하지 않는다.
- 시크릿 하드코딩 금지. `fastapi/.env`에서 로드하고 `.env.example`을 갱신한다.
- 동기 blocking I/O 금지. 카카오 호출은 **async httpx**.
- **`auth`는 `kingsman`을 임포트하지 않는다.** 유저 저장 경로는 §9 결정 필요.
- 네이밍은 기존 영화/팝컬처 컨벤션을 따르되 인증 도메인 식별성을 해치지 않는 선에서.

---

## 5. 작업 순서

각 단계 완료 후 변경 요약을 출력하고 검증을 통과시킨 뒤 다음으로 간다.

### 5.1 설정 / 스키마

`fastapi/.env` + `fastapi/.env.example`에 추가(주석 포함):

| 키 | 용도 | 비고 |
|----|------|------|
| `KAKAO_OIDC_ISSUER` | `https://kauth.kakao.com` | 고정값이지만 테스트에서 갈아끼울 수 있게 |
| `KAKAO_OIDC_CONFIG_URL` | discovery URL | |
| `KAKAO_OIDC_CACHE_TTL_SECONDS` | 기본 21600(6h) | |
| `KAKAO_ALLOWED_AUD` | 허용 `aud` 목록(쉼표 구분) | 미설정 시 `KAKAO_CLIENT_ID` 단일값 |
| `ACCESS_TTL_WEB_MIN` / `REFRESH_TTL_WEB_DAYS` | 30 / 7 | |
| `ACCESS_TTL_MOBILE_MIN` / `REFRESH_TTL_MOBILE_DAYS` | 60 / 30 | |

`KAKAO_CLIENT_ID`, `REDIS_URL`, `JWT_PRIVATE_KEY`, `JWT_PUBLIC_KEY`, `SERVICE_AUD`는
**이미 있다. 다시 정의하지 않는다.**

스키마(`apps/auth/schemas.py`에 추가):

- `KakaoLoginRequest(id_token: str, platform: Platform, nonce: str)`
- `RefreshRequest`에 `platform: Platform` 추가
- `LogoutRequest(platform: Platform, refresh_token: str | None)`
- `TokenResponse`에 `platform` 추가
- `Platform`은 `StrEnum`(`MOBILE="mobile"`, `WEB="web"`)으로 `rbac.py`의 `Provider` 옆에 둔다.

**검증:** `python -m pytest apps/auth/tests/ -v` 기존 테스트 그린 유지. `platform` 누락 요청이 4xx.

### 5.2 OIDC 검증 모듈

`apps/auth/oidc/kakao_verifier.py` (신규). discovery/JWKS 캐싱, 서명 검증,
`iss`/`aud`/`exp`/`nonce` 검증, 검증된 클레임 → `KakaoIdentity(sub: str, email: str | None, nickname: str | None)`.

- 카카오 `sub`는 **문자열로 다룬다.** 정수 캐스팅 금지.
- `email`은 동의 안 하면 없을 수 있다 → `None` 허용. 없다고 로그인을 막지 않는다.

**검증(단위 테스트, 외부 호출 없이 로컬 RSA 키로 토큰을 만들어 돌린다):**

| 케이스 | 기대 |
|--------|------|
| 유효 토큰 | 통과, `KakaoIdentity` 반환 |
| 서명 위조 | 실패 |
| `aud` 불일치 | 실패 |
| 만료 | 실패 |
| `nonce` 불일치 / 누락 | 실패 |
| `kid` miss → JWKS 1회 갱신 후 성공 | 갱신 호출 **정확히 1회** |
| JWKS 조회 실패 + 캐시 없음 | 503 계열 예외 |

### 5.3 Redis 세션 저장소

`apps/auth/store/refresh_store.py` (신규) — §3.3 구조.
`save_refresh(sub, platform, meta)` / `get_refresh(sub, platform)` / `revoke(sub, platform)`.

**검증:** 기존 테스트의 monkeypatch 방식(또는 fakeredis)으로,
`web` 저장 후 `revoke(mobile)` → `web` 생존. 반대도 성립. `exp` 지난 슬롯은 `get`이 `None`.

### 5.4 유저 서비스 연동

`KakaoIdentity.sub` 기준 조회 → 없으면 가입, 있으면 로그인. 매핑 대상은 `kingsman_users`
(`oauth_provider="kakao"`, `oauth_subject=sub`, `UNIQUE`가 이미 걸려 있다).
**접근 경로는 §9 결정 사항이다.** 정해지기 전까지는 인터페이스(포트)만 두고 진행한다.

**검증:** 같은 `sub`로 두 번 로그인 → 행이 1개. `email`/`nickname` 변경 시 갱신할지 무시할지 정책대로 동작.

### 5.5 토큰 발급 / 검증

`core/security.py`: 발급부에 `platform` 인자와 클레임 추가, TTL을 인자로 받게 확장.
검증부(`TokenPayload` / `RefreshPayload`)에 `platform` 노출. 정책 판정은 `auth`에서.

**검증:** 발급된 access/refresh를 디코드해 `sub`, `platform`, `jti`, `iat`, `exp` 존재 확인.
`api` 쪽 검증 경로(`core.dependencies`)가 기존 토큰으로 계속 통과하는지 확인.

### 5.6 엔드포인트

| 엔드포인트 | 동작 | 실패 |
|-----------|------|------|
| `POST /auth/kakao/login` | §3.1 전 과정 | id_token 불량 → 401 / `platform` 누락 → 400 / JWKS 확보 불가 → 503 |
| `POST /auth/refresh` | 서명 검증 → **platform 클레임 ↔ 요청 platform 일치** → Redis 슬롯 `th` 대조 → 로테이션 | 불일치·미존재 → 401 |
| `POST /auth/logout` | 해당 platform 슬롯만 `HDEL` | 토큰 불량이어도 200(멱등) |

에러 응답의 사용자 노출 메시지는 **한국어**로 쓴다(기존 라우터와 동일).

**검증:** `apps/auth/tests/`에 위 표의 각 실패 케이스 테스트. 성공 응답에 `platform` 포함.

### 5.7 회귀 확인

§7 시나리오를 전부 통과시킨다.

---

## 6. 완료 기준

- [ ] 유효한 카카오 `id_token`으로 로그인 시 자체 JWT(access/refresh) 발급, 최초 유저 DB 저장.
- [ ] 서명 위조 / `aud` 불일치 / 만료 / `nonce` 불일치 → 전부 **401**.
- [ ] 기본 로그인 경로에서 KAPI(`/v2/user/me`) 호출이 발생하지 않음.
- [ ] `platform` 누락 요청 → **400**(FastAPI 기본 422를 쓸지 400으로 통일할지 §9).
- [ ] 모바일/웹 refresh·logout이 서로에게 영향 없음.
- [ ] `auth:session:{sub}` Hash에 `web`/`mobile` 필드가 독립 존재·삭제됨.
- [ ] 리프레시 **원문이 Redis에 평문 저장되지 않음**(해시 + 메타만).
- [ ] JWKS/discovery가 캐싱되며 `kid` miss에만 갱신됨.
- [ ] 시크릿·개인키가 코드에 하드코딩되지 않고 `.env.example`이 갱신됨.
- [ ] `python -m pytest`, `lint-imports`, `python scripts/validate_harness.py` 통과.
      (`pytest.ini`의 `testpaths`에 `apps/auth/tests`가 이미 포함돼 있다.)

---

## 7. 회귀 시나리오

| # | 시나리오 | 기대 |
|---|----------|------|
| 1 | mobile 로그인 → 받은 refresh로 `platform="web"` refresh 시도 | 401, 두 슬롯 모두 무사 |
| 2 | web·mobile 둘 다 로그인 → `logout(mobile)` | mobile 401, **web은 계속 refresh 성공** |
| 3 | mobile refresh 로테이션 후 **이전** refresh 재사용 | 401 + mobile 슬롯 폐기, web 생존 |
| 4 | JWKS `kid` 롤오버(캐시 miss) | 1회 갱신 후 로그인 성공 |
| 5 | 카카오 discovery 응답 지연/실패 + 캐시 유효 | 캐시로 로그인 성공 |
| 6 | 카카오 discovery 실패 + 캐시 없음 | 503, 401로 뭉개지 않음 |
| 7 | `platform` 클레임 없는 구 토큰으로 refresh | 401 (재로그인 유도) |

---

## 8. 범위 밖

- KAPI 상세 프로필 조회(카카오 access token 기반) — 확장 지점만 남긴다.
- 웹 프론트의 쿠키/CSRF 정책, 프론트엔드 코드.
- 애플/구글 등 타 소셜 — 동일 검증 인터페이스로 확장 가능하게만 설계.
- n8n / EXAONE 이상탐지 연동.
- 기존 `POST /auth/login`(인가 코드 스텁)의 실제 프로바이더 연동.
- 같은 플랫폼 다중 기기 동시 세션.

---

## 9. 가정 / 결정 필요

**가정(그대로 진행)**

- access/refresh TTL: web 30m/7d, mobile 60m/30d. env로 분리하므로 변경 자유.
- 리프레시 로테이션 적용(재발급 시 이전 refresh 무효).
- Redis 값은 원문의 SHA-256 + `jti` + `iat` + `exp` JSON.
- `nonce`는 필수.
- 카카오 `sub`는 문자열.

**확정된 결정 (2026-08-03, 구현 반영 완료)**

1. **모바일과 웹은 같은 카카오 앱을 쓴다.** `aud` 검증은 기존 `KAKAO_CLIENT_ID` 하나로 한다.
   허용 aud 목록(`KAKAO_ALLOWED_AUD`)은 만들지 않았다 — 필요해지면 그때 넣는다.
2. **`auth`가 `kingsman_users`에 직접 접근한다((a)안).** `apps/auth/identity.py`가 kingsman의
   `UserRepository`를 재사용해 `user_id` 생성 규칙(`{provider}_{subject}`)을 웹 경로와 맞춘다.
   `.importlinter`의 spoke-to-spoke 계약에 `auth`는 source에 없어 위반이 아니다.
   반대 방향(영화 앱 → `apps.auth`)은 여전히 금지다.
3. **리프레시 재사용 감지 시 폐기 범위 = 해당 플랫폼 슬롯만.** 모바일 사고가 웹 세션을 끊지 않는다.
4. **`platform` 누락은 400.** `auth_main.py`에 `RequestValidationError` 핸들러를 두어
   auth 서비스의 422를 400으로 바꾼다(api 서비스는 그대로 422).
5. 기존 `POST /auth/login`은 `platform` 필드를 받되 **기본값 `web`**, `GET /auth/callback/{provider}`는
   브라우저 경로이므로 **web 고정**이다.
