---
type: spoke
app: dumb_and_dumber
links:
  - star_craft
---

# FAST-004 — S3 영수증 자동 OCR 가계부 파이프라인 (백엔드)

사용자가 가계부 화면에 진입하면 S3의 사용자 폴더에 쌓인 **미처리 영수증 이미지**를 감지하고,
OCR → 파싱 → 저장을 거쳐 결제 정보를 프론트로 반환하는 인바운드/아웃바운드 파이프라인의 하네스 스펙이다.

- 기준일: 2026-08-04
- 대상 앱: `fastapi/apps/dumb_and_dumber/` (현재 **빈 스켈레톤**) + `fastapi/.env.example`
- **이 문서는 스펙이며 구현 코드를 포함하지 않는다.** 각 단계의 "검증"으로 완료를 판정한다.
- 문서 제목의 *reverse* 는 원본 지시서(§2)를 저장소 현실에 맞게 **역방향으로 재작성**했다는 뜻이다.

---

## 0. 역할

`dumb_and_dumber` 스포크를 처음으로 살아 있는 앱으로 만드는 백엔드 엔지니어 관점의 작업 지시서다.
§5 작업 순서를 단계별로 진행하고, 각 단계마다 **변경 파일과 이유**를 요약한 뒤 다음으로 넘어간다.
불명확한 지점은 임의로 확장하지 말고 §9의 "결정 필요"에 올린 뒤 가정을 명시하고 진행한다.

---

## 1. 저장소 현황 — 이미 있는 것

원본 스펙은 "S3 어댑터를 새로 만든다"를 전제하지만, 저장소에는 S3 접근 경로가 **이미 세 개** 있다.
아래를 먼저 읽지 않으면 네 번째 경로를 만들게 된다.

| 위치 | 현재 하는 일 | 이번 작업에서의 취급 |
|------|--------------|----------------------|
| `core/matrix/aws_tank_s3_manager.py` | `Keymaker`로 `AWS_ACCESS_KEY_ID`/`SECRET`/`AWS_DEFAULT_REGION`을 읽어 boto3 클라이언트 싱글톤 생성. `list_bucket_names()`만 노출 | **재사용한다** — 자격증명 로딩의 단일 출처 |
| `star_craft/adapter/outbound/s3/s3_image_storage_gateway.py` | `VISION_S3_BUCKET` + `AWS_REGION`. `asyncio.to_thread`로 동기 boto3를 감싸는 패턴 | **패턴만 참고**. spoke→spoke 금지라 임포트 불가 |
| `silicon_valley/adapter/outbound/s3/s3_image_storage_adapter.py` | `S3_BUCKET`. 버킷 미설정 시 `ImageStorageError` | 패턴만 참고 |
| `core/dependencies.py` | `get_current_user` → `TokenPayload`(`sub`, `roles`, `jti`), `RoleChecker(Role.USER)` | **유일한 인증 접점** |
| `core/matrix/grid_neo_theone_base.py` | SQLAlchemy `Base`. 앱 시작 시 `create_all_tables()`가 테이블 자동 생성 | ORM 모델 정의에 사용 |
| `apps/dumb_and_dumber/` | 디렉터리 뼈대만 존재. `.py`는 전부 빈 `__init__.py`. `adapter/inbound/api/__init__.py`에 "라우터가 생기면 여기서 `dumb_and_dumber_router`로 묶는다"는 주석만 있음 | **이번 작업의 무대** |

즉 이번 작업은 "S3 클라이언트 구축"이 아니라 **기존 자격증명 경로 위에 도메인 파이프라인을 얹는 일**이다.

### 1.1 착수 전에 고쳐야 하는 저장소 결함 2건

작업과 직접 얽혀 있어 먼저 정리하지 않으면 하네스 검증이 의미를 잃는다.

1. **허브 문서가 엉뚱한 앱에 들어 있다.** `apps/dumb_and_dumber/_docs/CLAUDE.md`의 내용이 실제로는
   star_craft 허브 문서이며 frontmatter가 `type: hub / app: star_craft`다. 반면
   `apps/star_craft/_docs/CLAUDE.md`는 **0바이트**다. 이 상태로 이 앱에 스포크 문서를 추가하면
   같은 디렉터리에서 hub와 spoke가 동시에 선언된다.
   → §5.0에서 문서를 제자리로 옮긴다.
2. **`dumb_and_dumber`가 하네스에 등록돼 있지 않다.** `.importlinter`의 `root_packages`와
   `auth-isolation` 계약에는 있지만, **`star-topology-no-spoke-to-spoke` 계약의
   `source_modules`/`forbidden_modules`에는 없고**, `scripts/validate_harness.py`의 `SPOKE_APPS`에도,
   `pytest.ini`의 `testpaths`에도 없다. 지금 코드를 넣으면 **spoke→spoke 임포트가 검출되지 않는다.**
   → §5.0에서 등록한다.

> 참고: 이동 후 `apps/star_craft/_docs/CLAUDE.md`의 "Hub 확장 규칙" 1·2번 항목은
> `raynor_spoke_registry_repository.py` / `raynor_spoke_registry_tools.py`를 가리키는데
> 두 파일은 현재 존재하지 않는다(star_craft는 `vision_router`/`semantic_router` 구성으로 바뀌었다).
> **이번 작업 범위가 아니므로 고치지 않는다.** 3·4·5번 항목만 수행한다.

---

## 2. 원본 스펙과 저장소의 차이 — 착수 전 확정 사항

원본 지시서를 그대로 실행하면 저장소와 충돌하는 지점이 일곱 군데 있다. 아래로 대체한다.

### 2.1 스펙의 언어·네이밍이 Java/Spring 관례다

- 스펙: `ReceiptController`, `S3StorageAdapter`, `ClovaOcrAdapter`, camelCase 필드.
- 실제: Python/FastAPI. 라우터는 `*_router`, 유스케이스 구현체는 `*_interactor`,
  아웃바운드는 `*_repository` / `*_gateway` / `*_adapter`. 파일·필드는 snake_case.
- 더해 이 저장소는 파일·클래스·라우터 prefix에 **영화 캐릭터 이름**을 bounded context 식별자로 쓴다.
- **→ §3.1의 캐스팅 표를 따른다.** `Controller` 접미사를 쓰지 않는다.

### 2.2 `GET`인데 부작용이 있다 (가장 중요)

- 스펙: `GET /api/v1/ledger/receipts/auto-process`. 그런데 이 호출은 OCR을 돌리고,
  DB에 행을 쓰고, S3 객체를 `processed/`로 **이동**시킨다.
- GET은 안전(safe)해야 한다. 브라우저·프록시·`Link rel=prefetch`가 임의로 재호출할 수 있고,
  재시도가 중복 처리로 이어진다. 프론트가 "화면 진입 시" 호출하므로 리마운트마다 발화한다.
- **→ `POST`로 바꾼다.** 경로는 §2.3.
  GET을 유지해야 한다면 부작용을 분리해야 한다(조회 GET + 처리 POST) → §9 결정 필요.

### 2.3 `/api/v1/ledger/...` 경로는 이 저장소의 라우팅 규칙이 아니다

- 실제: `main.py`가 `app.include_router(x_router, prefix="/api")`로 붙이고, 앱 라우터가 자체 prefix를 갖는다
  (`star_craft_router = APIRouter(prefix="/star-craft")`). `v1`은 **패키지 이름일 뿐 URL에 나타나지 않는다.**
- **→ `POST /api/dumb-and-dumber/receipts/auto-process`.**
  파일은 관례대로 `adapter/inbound/api/v1/` 아래에 둔다.

### 2.4 응답이 영수증 1건인데 요구사항은 폴더 스캔이다

- 스펙: `data`가 단일 객체(`receiptId`, `storeName`, …). 그런데 A항은 "이미지 **목록** 조회"다.
  폴더에 3장이 있으면 무엇을 반환하는지 정의돼 있지 않다.
- **→ `data.receipts`를 배열로 만든다.** 1건일 때도 배열이다.
  프론트 분기 코드를 늘리는 단건/배열 혼합 응답은 만들지 않는다.
- 1회 호출당 처리 상한(`RECEIPT_MAX_BATCH`, 기본 5)을 둔다. 상한을 넘으면 오래된 순으로 자르고
  `hasMore: true`를 함께 준다. OCR은 외부 유료 호출이라 무한 루프가 곧 비용이다.

### 2.5 `userId`를 그대로 S3 키에 넣을 수 없다

- 실제: JWT의 `sub`는 `{provider}_{subject}` 형식이다(FAST-003 §9 결정 2).
- 이 값을 검증 없이 `receipts/{userId}/`로 이어 붙이면 경로 조작에 노출된다.
  현재 발급 규칙에서는 `/`나 `..`가 들어가지 않지만, **키 조립부는 발급 규칙을 신뢰하지 않는다.**
- **→ `^[A-Za-z0-9_-]{1,128}$`를 통과한 `sub`만 키에 넣는다.** 불통과 시 400.
  이 검증은 도메인 값 객체(`ReceiptKey`)에 두어 어댑터가 우회할 수 없게 한다.

### 2.6 인증은 라우터가 아니라 include 시점에 건다

- 스펙: "Request Headers: `Authorization: Bearer`, Context에서 `userId` 추출".
- 실제 패턴: `main.py`에서 `dependencies=[Depends(RoleChecker(Role.USER))]`로 라우터 전체에 인가를 건다
  (kingsman 선례). `sub`가 필요한 핸들러만 `Depends(get_current_user)`를 추가로 받는다.
- **→ 라우터 안에 토큰 파싱 코드를 쓰지 않는다.** `apps.auth`는 임포트 금지다(`.importlinter` 계약).

### 2.7 boto3는 동기 라이브러리다

- 실제: `fastapi/CLAUDE.md`의 async 원칙 — I/O는 `async def`이지만 boto3 호출 자체는 블로킹이다.
- **→ 모든 boto3 호출은 `await asyncio.to_thread(...)`로 감싼다.**
  `S3ImageStorageGateway`가 이미 이 형태다. `aioboto3`를 새로 도입하지 않는다.
- 반대로 **파서는 순수 CPU 연산이므로 `async`를 붙이지 않는다.** 정규식에 `async def`를 붙이면
  비동기인 척하는 블로킹 코드가 된다.

---

## 3. 아키텍처 결정

### 3.1 캐스팅 (dumb_and_dumber)

영화 «덤 앤 더머»의 핵심 소품은 **돈이 든 서류가방**이고, 로이드와 해리는 그 돈을 쓴 자리마다
**IOU 쪽지(영수증)** 를 채워 넣는다. 이 앱의 도메인과 그대로 겹치므로 캐스팅에 사용한다.

| 캐릭터 | 배역 | 레이어 |
|--------|------|--------|
| `lloyd` (로이드 크리스마스) | 가방을 열고 쪽지를 한 장씩 꺼낸다 — 자동 처리 오케스트레이션 | 입력 포트 / 인터랙터 |
| `harry` (해리 던) | 서류가방 자체를 다룬다 — S3 목록 조회·다운로드·`processed/` 이동 | 출력 포트 / S3 어댑터 |
| `mary` (메리 스완슨) | 가방의 진짜 주인, 원본 문서를 읽어낸다 — OCR 엔진 호출 | 출력 포트 / OCR 어댑터 |
| `petey` (앵무새 페티) | 읽어낸 텍스트를 항목으로 옮겨 적는다. 머리가 없으면 티가 난다 — 파싱·검수 플래그 | 도메인 서비스 |
| `mental` (조 "멘탈" 멘탈리노) | 누가 얼마를 썼는지 장부에 적고 중복을 대조한다 — 영수증 저장소 | 출력 포트 / PG 레포지터리 |

### 3.2 파이프라인

```text
[Web] 가계부 화면 진입
      │  POST /api/dumb-and-dumber/receipts/auto-process
      │  Authorization: Bearer <access_token>
      ▼
[api] RoleChecker(Role.USER) → get_current_user → sub
      ▼
[lloyd 인터랙터]
   1) ReceiptKey(sub) 검증·조립                      → 실패 시 400
   2) harry.list_unprocessed(prefix)                 → S3 ListObjectsV2 (최대 RECEIPT_MAX_BATCH)
   3) mental.find_by_object_keys(keys)               → 이미 처리된 키 제외 (멱등성)
   4) 남은 키마다:
        harry.fetch(key)          → bytes
        mary.read(bytes)          → OcrTextBlock[]   (원문 JSON은 저장하지 않는다)
        petey.parse(blocks)       → Receipt (순수)
        mental.save(receipt)      → DB 행
        harry.move_to_processed(key)
   5) harry.presign(processed_key) → imageUrl (TTL 10분)
      ▼
[Web] receipts[] 수신
```

- 4번 루프는 **영수증 단위로 커밋**한다. 3장 중 2번째가 실패해도 1번째 결과는 남는다.
  실패한 건은 S3에서 옮기지 않고 응답의 `failures[]`에 `objectKey`와 사유를 담아 돌려준다
  (조용히 사라지는 영수증을 만들지 않는다).
- OCR 원문 JSON은 DB에 저장하지 않는다. 개인 결제 정보를 필요 이상으로 남기지 않는다.

### 3.3 S3 레이아웃과 멱등성

```text
s3://{RECEIPT_S3_BUCKET}/
  receipts/{sub}/unprocessed/{uuid}.jpg      ← 클라이언트가 업로드 (업로드 경로는 이번 범위 밖)
  receipts/{sub}/processed/{uuid}.jpg        ← 처리 완료 후 이동
```

원본 스펙은 "S3 이동 **또는** DB `is_processed: true`"라며 둘 중 하나를 고르게 했지만,
**둘 다 한다.** 실패 모드가 다르기 때문이다.

- DB 기록만: S3에 원본이 남아 매 호출마다 다시 목록에 잡히고 폴더가 무한히 커진다.
- 이동만: `move` 직후·DB 커밋 직전에 죽으면 영수증이 유실된다.
- **순서를 `DB 저장 → S3 이동`으로 고정한다.** 이동 실패 시 다음 호출에서 같은 키가 다시 잡히지만,
  3번의 `find_by_object_keys` 필터가 걸러내므로 **중복 OCR 호출이 발생하지 않는다.**
  이 순서를 뒤집으면 멱등성이 깨진다.

`is_processed` 불리언 컬럼은 두지 않는다. 행의 존재 자체가 처리 완료를 뜻한다.

### 3.4 OCR 어댑터

`MaryOcrEnginePort`는 `read(image: bytes, content_type: str) -> list[OcrTextBlock]` 하나만 갖는다.
구현체는 둘이다.

| 구현체 | 용도 |
|--------|------|
| `mary_clova_ocr_adapter.py` | 운영. CLOVA OCR General 호출(async httpx). `CLOVA_OCR_INVOKE_URL` + `X-OCR-SECRET` |
| `mary_fake_ocr_adapter.py` | 테스트·로컬. 고정 텍스트 블록 반환. 외부 호출·과금 없음 |

- 프로바이더 선택은 `RECEIPT_OCR_PROVIDER`(`clova` \| `fake`) 하나로 한다.
  Google Vision 어댑터는 **지금 만들지 않는다.** 포트가 있으므로 필요해질 때 파일 하나만 추가하면 된다.
- 저장소에 이미 있는 Gemini(멀티모달)를 쓰자는 대안은 §9 결정 필요에 올린다.
  키가 이미 있어 즉시 동작하지만, 영수증 OCR 정확도는 전용 엔진이 낫다.
- OCR 응답은 어댑터 경계에서 `OcrTextBlock(text, confidence, bbox)` 리스트로 정규화한다.
  **벤더 JSON 구조가 도메인·유스케이스로 새어 나가면 안 된다.**

### 3.5 파싱 규칙 (`petey`)

정규식·규칙 기반이며 **외부 의존이 전혀 없는 순수 함수**다(도메인 레이어).

| 필드 | 추출 규칙 | 실패 시 |
|------|-----------|---------|
| `store_name` | 상단 블록 중 사업자번호·전화번호 패턴이 아닌 첫 줄 | `None` + 플래그 |
| `transaction_date` | `YYYY-MM-DD`/`YYYY.MM.DD`/`YY/MM/DD` + `HH:mm(:ss)?` | `None` + 플래그 |
| `items` | `품목 수량 금액` 3열 패턴. 금액은 천 단위 쉼표 허용 | 빈 배열 + 플래그 |
| `total_amount` | `합계`/`총액`/`결제금액` 키워드 뒤 최대 금액 | `None` + 플래그 |
| `approval_number` | `승인번호` 뒤 6자리 이상 숫자 | `None` (**플래그 없음** — 선택 항목) |

- 금액은 **원 단위 정수**로 다룬다. `float`를 쓰지 않는다.
- `needs_manual_review`는 위 플래그의 OR이다. 별도 판정 로직을 만들지 않는다.
- 검산은 하되 값을 고치지 않는다: `sum(items.price) != total_amount`면 `needs_manual_review = True`.
  파서가 총액을 임의로 재계산해 덮어쓰면 사용자가 틀린 걸 알 방법이 없다.

### 3.6 응답 형식

원본 스펙의 camelCase를 유지한다(프론트가 Next.js/TypeScript다).
Python 코드는 snake_case로 쓰고 **Pydantic alias로만 변환**한다
(`sherlock_homes`의 `populate_by_name: True` 선례).

```json
{
  "success": true,
  "data": {
    "receipts": [
      {
        "receiptId": "rcpt_12345678",
        "imageUrl": "https://...(presigned, TTL 10m)",
        "storeName": "클린카페 서울점",
        "transactionDate": "2026-08-04T10:00:00",
        "items": [
          { "name": "아메리카노", "quantity": 2, "price": 9000 },
          { "name": "조각 케이크", "quantity": 1, "price": 7500 }
        ],
        "totalAmount": 16500,
        "needsManualReview": false
      }
    ],
    "hasMore": false,
    "failures": []
  }
}
```

- `imageUrl`은 **presigned URL**이다. 스펙 예시처럼 `https://s3.amazonaws.com/...` 공개 URL을 주려면
  버킷을 퍼블릭으로 열어야 한다. 영수증은 개인 결제 정보다 — 버킷은 비공개를 유지한다.
- `receiptId`는 `rcpt_` + UUID4 hex 8자. DB PK(정수)를 노출하지 않는다.

---

## 4. 제약

- **spoke → spoke 임포트 금지.** 가계부가 `kingsman`의 유저 테이블을 참조하고 싶어지겠지만 금지다.
  `user_id`는 JWT `sub` **문자열로만** 저장하고 FK를 걸지 않는다. 조인이 필요하면 hub(`star_craft`)를 경유한다.
- `apps.auth` 임포트 금지. 인증 접점은 `core.dependencies`뿐이다.
- 의존성 방향 `adapter → app → domain`. `domain`/`app`이 boto3·httpx·SQLAlchemy를 임포트하지 않는다.
- 시크릿 하드코딩 금지. `fastapi/.env`에서 읽고 `fastapi/.env.example`을 같은 커밋에서 갱신한다.
  같은 키를 파일 안에 두 번 정의하지 않는다.
- 동기 blocking I/O 금지. boto3는 `asyncio.to_thread`, HTTP는 async httpx.
- OCR 원문 JSON·이미지 바이트를 로그에 남기지 않는다. 로그에는 `objectKey`와 처리 결과만 남긴다.
- 사용자에게 노출되는 에러 메시지는 **한국어**로 쓴다.
- 기존 S3 코드(`star_craft`/`silicon_valley`/`aws_tank_s3_manager`)를 **리팩터링하지 않는다.**
  환경변수 이름 불일치는 §9에 기록만 하고 손대지 않는다.

---

## 5. 작업 순서

각 단계 완료 후 변경 요약을 출력하고 검증을 통과시킨 뒤 다음으로 간다.

### 5.0 하네스 등록 (코드보다 먼저)

§1.1의 결함 2건을 정리한다.

1. `apps/dumb_and_dumber/_docs/CLAUDE.md`의 내용을 `apps/star_craft/_docs/CLAUDE.md`(현재 0바이트)로 옮긴다.
2. `apps/dumb_and_dumber/_docs/CLAUDE.md`를 이 앱의 스포크 문서로 새로 쓴다
   (frontmatter `type: spoke` / `app: dumb_and_dumber` / `links: [star_craft]`, §3.1 캐스팅 표 포함).
3. `.importlinter`의 `star-topology-no-spoke-to-spoke` 계약 `source_modules`·`forbidden_modules`에
   `dumb_and_dumber` 추가. `clean-arch-adapter-to-domain` 계약에 `dumb_and_dumber.domain`/`.app` →
   `dumb_and_dumber.adapter` 항목 추가.
4. `scripts/validate_harness.py`의 `SPOKE_APPS`에 `dumb_and_dumber` 추가.
5. `pytest.ini`의 `testpaths`에 `apps/dumb_and_dumber/tests` 추가.
6. `fastapi/CLAUDE.md`의 앱 목록 표에 `dumb_and_dumber` 행을 추가한다(현재 표에 없다).

**검증:** `lint-imports`, `python scripts/validate_harness.py`, `markdownlint "**/_docs/**/*.md"` 3종 통과.
`python -m pytest`가 새 testpath에서 수집 오류 없이 통과.

### 5.1 환경 변수

`fastapi/.env` + `fastapi/.env.example`에 추가(주석 포함).

| 키 | 용도 | 비고 |
|----|------|------|
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | S3 자격증명 | **코드는 이미 읽는데 `.env.example`에 없다.** 이번에 추가 |
| `AWS_DEFAULT_REGION` | boto3 표준 리전 변수 | 기본 `ap-northeast-2` |
| `RECEIPT_S3_BUCKET` | 영수증 버킷 | 미설정 시 기동은 되고 호출 시 503 |
| `RECEIPT_S3_PREFIX` | 기본 `receipts` | |
| `RECEIPT_PRESIGN_TTL_SECONDS` | 기본 600 | |
| `RECEIPT_MAX_BATCH` | 1회 처리 상한, 기본 5 | §2.4 |
| `RECEIPT_OCR_PROVIDER` | `clova` \| `fake`, 기본 `fake` | 기본값을 `fake`로 두어 키 없이 개발 가능 |
| `CLOVA_OCR_INVOKE_URL` / `CLOVA_OCR_SECRET_KEY` | CLOVA OCR | `provider=clova`일 때만 필수 |

`DATABASE_URL`, `SERVICE_AUD`, `JWT_PUBLIC_KEY`는 **이미 있다. 다시 정의하지 않는다.**

**검증:** `.env` 없이 앱이 기동된다(임포트 시점에 시크릿을 읽지 않음). `RECEIPT_S3_BUCKET` 미설정 상태로
엔드포인트 호출 → 한국어 메시지와 함께 503.

### 5.2 도메인 (외부 의존 0)

`apps/dumb_and_dumber/domain/` — `entities/receipt.py`, `value_objects/money.py`,
`value_objects/receipt_item.py`, `value_objects/receipt_key.py`, `petey_receipt_parser.py`.

**검증(`tests/domain/`, DB·네트워크 없이):**

| 케이스 | 기대 |
|--------|------|
| 정상 영수증 텍스트 | 5개 필드 전부 추출, `needs_manual_review=False` |
| 총액 누락 | `total_amount=None`, `needs_manual_review=True` |
| `sum(items) != total` | 값 보정 없이 `needs_manual_review=True` |
| 승인번호만 누락 | `needs_manual_review=False` (선택 항목) |
| 금액 `16,500` | `16500` 정수 |
| `sub`에 `../` 포함 | `ReceiptKey` 생성 실패 |
| `sub`가 128자 초과 | 생성 실패 |

### 5.3 포트 + DTO

`app/ports/input/lloyd_receipt_auto_process_use_case.py`,
`app/ports/output/{harry_briefcase_storage_port,mary_ocr_engine_port,mental_receipt_ledger_port}.py`,
`app/dtos/lloyd_receipt_auto_process_dto.py`.

**검증:** `lint-imports` 통과. 포트 파일에 boto3·httpx·sqlalchemy 임포트가 **없다**(grep으로 확인).

### 5.4 인터랙터

`app/use_cases/lloyd_receipt_auto_process_interactor.py` — §3.2의 1~5단계.

**검증(`tests/app/use_cases/`, 세 포트 전부 페이크로):**

| 케이스 | 기대 |
|--------|------|
| 미처리 3장 | 3건 반환, `mary.read` 3회 호출 |
| 미처리 0장 | `receipts: []`, OCR 호출 **0회** |
| 이미 DB에 있는 키 포함 | 해당 키는 OCR 호출 **없이** 건너뜀 |
| 2번째 OCR 실패 | 1·3번은 저장·이동됨, 2번은 `failures[]`에 등장, S3 이동 없음 |
| DB 저장 후 S3 이동 실패 | 다음 호출에서 OCR 재호출 **없이** 필터됨 |
| 미처리 10장, `MAX_BATCH=5` | 5건 + `has_more=True` |

### 5.5 아웃바운드 어댑터

- `adapter/outbound/s3/harry_briefcase_s3_adapter.py` — `list_unprocessed` / `fetch` /
  `move_to_processed`(`copy_object` + `delete_object`) / `presign`. 전부 `asyncio.to_thread`.
  자격증명은 `core.matrix.aws_tank_s3_manager.get_client()`를 쓴다.
- `adapter/outbound/ocr/mary_clova_ocr_adapter.py`, `mary_fake_ocr_adapter.py`.
- `adapter/outbound/orm/receipt_orm.py` — 테이블 `dumb_and_dumber_receipts`,
  `UNIQUE(user_id, object_key)`. `create_all_tables()`가 자동 생성한다.
- `adapter/outbound/pg/mental_receipt_ledger_pg_repository.py`.

**검증:** 스텁 클라이언트(또는 `moto`)로 `move_to_processed`가 copy→delete 순서로 호출되는지,
copy 실패 시 delete가 호출되지 **않는지** 확인. CLOVA 어댑터는 httpx `MockTransport`로 응답 정규화만 검증.

### 5.6 인바운드 어댑터 + DI

- `adapter/inbound/api/schemas/receipt_schema.py` — §3.6 camelCase alias.
- `adapter/inbound/api/v1/lloyd_receipt_router.py` — `APIRouter(prefix="/receipts", tags=["receipts"])`.
- `adapter/inbound/api/__init__.py` — 현재의 안내 주석을 지우고 `dumb_and_dumber_router`
  (`prefix="/dumb-and-dumber"`)로 묶는다.
- `dependencies/lloyd_receipt_auto_process_provider.py` — `RECEIPT_OCR_PROVIDER`로 OCR 구현체 선택.
- `main.py` — `app.include_router(dumb_and_dumber_router, prefix="/api",
  dependencies=[Depends(RoleChecker(Role.USER))])`. kingsman 아래에 추가한다.

**검증:** 토큰 없이 호출 → 401. `USER` 역할 없는 토큰 → 403. `/docs`에 엔드포인트 노출.
응답 JSON 키가 camelCase.

### 5.7 회귀 확인

§7 시나리오를 전부 통과시킨다.

---

## 6. 완료 기준

- [ ] `POST /api/dumb-and-dumber/receipts/auto-process`가 미처리 영수증을 배열로 반환한다.
- [ ] 인증 없음 → 401, 권한 부족 → 403, 잘못된 `sub` → 400, 버킷 미설정 → 503.
- [ ] 같은 영수증이 **두 번 OCR되지 않는다**(반복 호출 시 OCR 호출 0회).
- [ ] DB 저장 → S3 이동 순서가 지켜지고, 이동 실패가 데이터 유실로 이어지지 않는다.
- [ ] 파싱 실패 항목이 `needsManualReview=True`로 표시되며, 파서가 총액을 임의 보정하지 않는다.
- [ ] `imageUrl`이 presigned URL이며 버킷이 퍼블릭이 아니다.
- [ ] `domain`/`app` 레이어에 boto3·httpx·SQLAlchemy 임포트가 없다.
- [ ] `RECEIPT_OCR_PROVIDER=fake`로 **외부 호출·과금 없이** 전체 파이프라인 테스트가 돈다.
- [ ] `.env.example`에 AWS·CLOVA·RECEIPT 키가 추가됐고 실제 시크릿은 커밋되지 않았다.
- [ ] `python -m pytest`, `lint-imports`, `markdownlint`, `python scripts/validate_harness.py` 전부 통과.

---

## 7. 회귀 시나리오

| # | 시나리오 | 기대 |
|---|----------|------|
| 1 | 영수증 2장 업로드 후 API 2회 연속 호출 | 1회차 2건 반환, **2회차 0건 + OCR 호출 0회** |
| 2 | A 사용자 토큰으로 호출 | B 사용자 폴더의 객체가 응답에 절대 없음 |
| 3 | `sub`에 `../` 주입 시도 | 400, S3 호출 발생 안 함 |
| 4 | OCR 응답이 빈 블록 배열 | `needsManualReview=True`로 저장, 500 아님 |
| 5 | S3 `move_to_processed` 실패 | DB 행 존재, 다음 호출에서 OCR 없이 필터 |
| 6 | 미처리 10장 / `MAX_BATCH=5` | 5건 + `hasMore=True`, 다음 호출에서 나머지 5건 |
| 7 | `RECEIPT_S3_BUCKET` 미설정 | 503 + 한국어 메시지, 스택트레이스 노출 없음 |
| 8 | `dumb_and_dumber`에서 `kingsman` 임포트 추가 | `lint-imports` **실패** (5.0 등록이 실제로 동작하는지 확인) |

---

## 8. 범위 밖

- **클라이언트의 S3 업로드 경로**(presigned PUT 발급 등). 이 스펙은 이미 올라온 파일만 다룬다.
- 프론트엔드(Next.js) 화면·상태 관리. 짝 문서는 별도로 만든다.
- 수동 수정 API(`needsManualReview` 건을 사용자가 고치는 엔드포인트).
- 카테고리 자동 분류, 월별 집계, 예산 등 가계부 본체 기능.
- Google Vision / Gemini OCR 어댑터 — 포트만 열어 두고 구현하지 않는다.
- 기존 S3 코드 3종의 통합 리팩터링(§9에 기록만).
- `star_craft` 허브 문서의 "Hub 확장 규칙" 1·2번 죽은 참조 정리.

---

## 9. 가정 / 결정 필요

**가정(그대로 진행)**

- 호스팅 앱은 `dumb_and_dumber` 스포크다. 영화의 "서류가방 + IOU 쪽지"가 도메인과 맞고,
  이 앱이 유일하게 비어 있는 헥사고날 스켈레톤이다.
- 금액은 원 단위 정수. 통화는 KRW 고정(필드로 노출하지 않는다).
- `transactionDate`는 타임존 없는 로컬 시각으로 저장·반환한다(영수증에 TZ 정보가 없다).
- OCR 원문 JSON은 저장하지 않는다.
- `RECEIPT_OCR_PROVIDER` 기본값은 `fake`다. 운영 `.env`에서 `clova`로 바꾼다.

**결정 필요 (착수 전 확인)**

1. **`GET` → `POST` 변경을 수용하는가?** (§2.2) 프론트 계약이 이미 GET으로 굳었다면
   "조회 GET + 처리 POST" 두 엔드포인트로 나눈다. 부작용 있는 GET을 그대로 두는 선택지는 권하지 않는다.
2. **OCR 프로바이더** — CLOVA(신규 계약·과금) vs 이미 키가 있는 Gemini 멀티모달.
   영수증 정확도는 CLOVA가 낫지만 Gemini는 오늘 바로 동작한다.
3. **응답 배열화**(§2.4)를 프론트가 수용하는가. 단건 유지가 확정이면 "가장 오래된 1건"으로 좁힌다.
4. **`AWS_REGION`(star_craft) vs `AWS_DEFAULT_REGION`(core·silicon_valley) 불일치.**
   이번엔 `AWS_DEFAULT_REGION`만 쓰고 star_craft는 건드리지 않는다. 통일 여부는 별건으로 결정.
5. **버킷을 기존 `S3_BUCKET`/`VISION_S3_BUCKET`과 공유할지 분리할지.**
   영수증은 개인 결제 정보라 **분리(`RECEIPT_S3_BUCKET`)** 를 전제로 썼다.
6. **영수증 보존 기간.** `processed/`가 무한히 쌓인다. S3 라이프사이클 규칙이 필요하지만
   버킷 정책은 이 저장소 밖이다.
