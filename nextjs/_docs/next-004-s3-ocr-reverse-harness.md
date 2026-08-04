# NEXT-004 — 가계부 영수증 자동 OCR 인식 화면 (프론트엔드)

가계부 화면 진입 시 백엔드의 자동 OCR 파싱 API를 호출해 S3에 쌓인 영수증 데이터를 불러오고,
사용자가 확인·수정한 뒤 저장하는 UI의 하네스 스펙이다.

- 기준일: 2026-08-04
- 대상: `nextjs/app/ledger/`, `nextjs/components/ledger/`, `nextjs/lib/`, `nextjs/hooks/`
- 짝 문서(백엔드): [`fastapi/_docs/fast-004-s3-ocr-reverse-harness.md`](../../fastapi/_docs/fast-004-s3-ocr-reverse-harness.md)
- **이 문서는 스펙이며 구현 코드를 포함하지 않는다.** 각 단계의 "검증"으로 완료를 판정한다.
- 제목의 *reverse* 는 원본 지시서(§2)를 저장소 현실에 맞게 **역방향으로 재작성**했다는 뜻이다.

> `nextjs/_docs/`는 온톨로지 하네스 대상이 아니다(`scripts/validate_harness.py`는 `fastapi/` 아래만
> 스캔한다). 기존 `darkmode-spec.md` / `react_rules.md`와 동일하게 frontmatter를 두지 않는다.

---

## 0. 역할

가계부 영수증 화면을 만드는 프론트엔드 엔지니어 관점의 작업 지시서다.
§5 작업 순서를 단계별로 진행하고, 각 단계마다 **변경 파일과 이유**를 요약한 뒤 다음으로 넘어간다.
불명확한 지점은 임의로 확장하지 말고 §9의 "결정 필요"에 올린 뒤 가정을 명시하고 진행한다.

이 화면은 **백엔드 FAST-004에 의존한다.** 백엔드가 `POST /api/dumb-and-dumber/receipts/auto-process`를
구현하기 전에는 §5.1~5.3(타입·API 계층·훅)까지만 진행하고 UI는 페이크 데이터로 검증한다.

---

## 1. 저장소 현황 — 이미 있는 것

원본 스펙은 TanStack Query·Formik·`src/` 디렉터리를 전제하지만 **셋 다 이 저장소에 없다.**
아래를 먼저 읽지 않으면 저장소에 없는 스택으로 코드를 쓰게 된다.

| 항목 | 실제 저장소 | 이번 작업에서의 취급 |
|------|-------------|----------------------|
| 데이터 페칭 | **TanStack Query 없음.** `fetch` + `useState`/`useEffect`가 12곳(`app/lesson/titanic/page.tsx`, `app/lesson/contacts/page.tsx` 등) | 라이브러리 추가 없이 커스텀 훅 하나로 처리 (§2.1) |
| 폼 | `react-hook-form@7.54` + `@hookform/resolvers` + `zod@3.24` **설치돼 있음**. 단 `useForm` 사용처는 `components/ui/form.tsx`(shadcn 래퍼)뿐 | 동적 품목 리스트 때문에 RHF를 쓴다 (§2.8) |
| UI 킷 | shadcn/ui 55개. `skeleton` / `spinner` / `table` / `form` / `badge` / `empty` / `card` / `input` / `calendar` / `alert` 전부 존재 | **전부 재활용.** 새 원시 컴포넌트를 만들지 않는다 |
| 디렉터리 | `src/` 없음. 루트에 `app/` `components/` `lib/` `hooks/`, alias `@/*` → `./*` | §2.2 |
| 백엔드 호출 | `process.env.NEXT_PUBLIC_API_URL` 또는 `NEXT_PUBLIC_API_BASE_URL`을 각 파일에서 개별로 읽음. 공용 API 클라이언트 없음 | `lib/receiptApi.ts`에 이 화면 몫만 모은다 |
| 인증 | **액세스 토큰을 다루는 코드가 없다** (§2.4) | **선행 과제.** §5.0 |
| 테마 | `app/layout.tsx`가 `ThemeProvider attribute="class"`. 모든 컴포넌트에 `dark:` 클래스 | 다크 모드 필수 (§2.7) |
| 토스트 | `hooks/use-toast.ts`, `components/ui/toaster.tsx`, `components/ui/sonner.tsx` 존재하나 **`<Toaster />`가 layout에 마운트돼 있지 않다** | 토스트를 쓰지 않는다 (§2.9) |
| 린트 | `package.json`에 `"lint": "eslint ."`가 있으나 **eslint 의존성도 설정 파일도 없다** | 검증은 `tsc` + `build` (§2.5) |

### 1.1 지켜야 하는 기존 규칙 문서

- `.claude/rules/typescript.md` — `type` 우선(`interface`/`enum` 지양), `any` 금지·`unknown`으로 좁히기,
  Props는 `<컴포넌트명>Props` 타입 + named export, 상수는 `as const`, 에러 메시지는 한국어.
- `nextjs/_docs/react_rules.md` — "useState를 많이 쓰지 않는다. 여러 입력 값은 상태 객체로 묶는다."
- `nextjs/_docs/darkmode-spec.md` — Tailwind `dark:` 클래스 방식.

---

## 2. 원본 스펙과 저장소의 차이 — 착수 전 확정 사항

원본 지시서를 그대로 실행하면 저장소와 충돌하는 지점이 아홉 군데 있다. 아래로 대체한다.

### 2.1 TanStack Query가 없다

- 스펙: "TanStack Query 또는 프로젝트 기본 상태관리 도구 활용."
- 실제: `package.json`에 없다. 이 저장소의 "기본 상태관리 도구"는 **`useState` + `fetch`**다.
- **→ 라이브러리를 추가하지 않는다.** `hooks/useAutoReceiptFetch.ts` 하나로
  `status: "idle" | "loading" | "success" | "error"` 유니언을 반환한다.
  화면 하나 때문에 전역 서버 상태 라이브러리를 도입하는 것은 이 저장소 규모에 과하다.
- 상태를 `useState` 네 개로 쪼개지 않는다(`react_rules.md`). **하나의 상태 객체**로 묶고
  `status` 유니언으로 판별한다. `isLoading` + `error` + `data` 불리언 조합은 불가능한 상태를 만든다.
- 도입 여부는 §9 결정 필요 1번.

### 2.2 `src/` 디렉터리가 없다

- 스펙: `src/api/receiptApi.ts`.
- 실제: 루트에 `app/` `components/` `lib/` `hooks/`가 있고 `@/*`가 `./*`를 가리킨다.
- **→ `lib/receiptApi.ts`, `hooks/useAutoReceiptFetch.ts`, `components/ledger/*`.**
  `src/`나 `app/api/`를 새로 파지 않는다.

### 2.3 엔드포인트가 백엔드 확정본과 다르다

- 스펙: `GET /api/v1/ledger/receipts/auto-process`.
- 백엔드 확정(FAST-004 §2.2·§2.3): **`POST /api/dumb-and-dumber/receipts/auto-process`**.
  OCR·DB write·S3 이동이라는 부작용이 있어 GET을 쓰지 않으며, `v1`은 URL에 나타나지 않는다.
- 저장 API `POST /api/v1/ledger/entries`는 **백엔드에 존재하지 않는다.**
  FAST-004 §8이 "수동 수정 API"를 명시적으로 범위 밖에 두었다.
  **→ [가계부 저장] 버튼은 이번 범위에서 완결되지 않는다.** §9 결정 필요 3번.

경로에 `dumb-and-dumber`가 들어가는 것은 백엔드의 **영화 캐릭터 네이밍 컨벤션**(`fastapi/CLAUDE.md`)
때문이다. 이 컨벤션은 백엔드 전용이므로 **프론트 라우트·컴포넌트 이름에 옮기지 않는다.**
프론트는 기존 관례대로 도메인 이름을 쓴다 → 라우트 `/ledger`, 컴포넌트 `components/ledger/`.

### 2.4 프론트엔드에 액세스 토큰이 없다 (가장 중요 · 블로킹)

- 스펙: 헤더 언급 없이 API만 호출하면 되는 것처럼 쓰여 있다.
- 실제: 이 엔드포인트는 `main.py`에서 `Depends(RoleChecker(Role.USER))`로 보호된다. 토큰 없으면 401이다.
- 그런데 저장소에 **토큰을 저장하거나 헤더에 싣는 코드가 한 줄도 없다.**
  - `components/auth/AuthPanel.tsx`의 `handleLogin`은 `onSuccess?.()`만 호출하는 스텁이다.
  - `components/auth/OAuthRedirectHandler.tsx`는 `?auth=success`를 보고 `/dashboard`로 보낼 뿐이다.
  - 기존 백엔드 fetch 12곳은 전부 인증 헤더가 없다(해당 엔드포인트가 공개라 문제되지 않았다).
- **쿠키로 우회할 수 없다.** `core/security.py`의 `COOKIE_KWARGS`는
  `domain=".ragtailor.com"` / `secure=True`인데 API는 **`api.ragtaylor.com`**이다.
  `ragtailor`와 `ragtaylor`는 **서로 다른 등록 도메인**이므로(오타가 아니라 별개 코드네임이다)
  쿠키가 API로 전송되지 않는다. 로컬 `localhost`에서는 `secure=True` + 도메인 불일치로 세팅조차 되지 않는다.
- **→ `Authorization: Bearer <access_token>` 헤더로 간다.** 토큰 확보·보관 경로가 **선행 과제**다(§5.0).
  이 화면 안에 로그인 로직을 만들어 넣지 않는다.

### 2.5 `pnpm lint`는 동작하지 않는다

- 스펙: "Lint 및 Type Check를 수행하세요."
- 실제: `"lint": "eslint ."`가 있지만 eslint가 `package.json` 의존성에도 `node_modules/.bin`에도 없고
  설정 파일도 없다. 실행하면 `ESLint looked for configuration files ...` 후 **exit code 2로 실패**한다.
- 더해 `next.config.mjs`의 `typescript.ignoreBuildErrors: true` 때문에
  **`pnpm build`는 타입 에러를 잡지 않는다.**
- **→ 검증은 두 명령을 모두 돌린다.**

  ```bash
  cd nextjs
  pnpm exec tsc --noEmit   # 타입 검사 (build가 대신해 주지 않는다)
  pnpm build               # 빌드·번들 검증
  ```

- eslint 설치는 이 작업 범위 밖이다. `nextjs/CLAUDE.md`의 `pnpm lint` 안내가 실제와 다르다는 사실만 기록한다.

### 2.6 Date/Time Picker 공통 컴포넌트가 없다

- 스펙: "결제 일시: Date/Time Picker".
- 실제: shadcn `calendar.tsx`(react-day-picker)는 **날짜만** 다룬다. 시각 입력 컴포넌트가 없다.
- **→ `<Input type="datetime-local">` 하나로 처리한다.** 브라우저 네이티브라 접근성·모바일 대응이 공짜다.
  `Calendar` 팝오버 + 시각 입력을 조합한 `DateTimePicker`를 새로 만들지 않는다 — 이 화면 하나를 위한
  추상화다(루트 CLAUDE.md §2 단순성 우선).
- 백엔드는 `"2026-08-04T10:00:00"`(타임존 없는 로컬 시각, FAST-004 §9)을 준다.
  `datetime-local`의 값 형식과 그대로 맞으므로 변환 로직이 필요 없다. `date-fns`를 끌어오지 않는다.

### 2.7 다크 모드는 선택이 아니다

- `app/layout.tsx`가 `ThemeProvider attribute="class" defaultTheme="light" enableSystem`으로 감싼다.
- **→ 새 컴포넌트의 모든 배경·테두리·텍스트에 `dark:` 대응을 단다.**
  기존 톤을 따른다: 배경 `dark:bg-[#111111]` / `dark:bg-[#1a1a1a]`, 테두리 `dark:border-gray-700`,
  텍스트 `dark:text-neutral-100` / `dark:text-neutral-300`, 강조색 `sky-600` → `dark:sky-400`.

### 2.8 폼은 react-hook-form을 쓰되, 이 화면에서만 쓴다

- 스펙: "React Hook Form / Formik 등". **Formik은 설치돼 있지 않으므로 후보가 아니다.**
- 기존 폼(`AuthPanel.tsx`)은 `FormData` + `Object.fromEntries` 방식이다. 단순 폼에는 그게 맞다.
- 그러나 이번 요구는 **동적 품목 리스트(행 추가·삭제) + 금액 합계 연동 + validation**이다.
  `FormData`로 하면 인덱스 관리 코드를 직접 짜게 된다. **`useFieldArray`가 정당한 선택이다.**
- `zod` + `@hookform/resolvers`가 이미 있으므로 `zodResolver`로 스키마 검증을 붙인다.
- **다른 화면의 폼을 RHF로 바꾸지 않는다**(루트 CLAUDE.md §3 정밀한 수정).

### 2.9 토스트를 쓰지 않는다

- `hooks/use-toast.ts`와 `components/ui/toaster.tsx`, `components/ui/sonner.tsx`가 모두 있지만
  **`app/layout.tsx`에 `<Toaster />`가 마운트돼 있지 않다.** 지금 `toast()`를 호출하면 아무것도 안 뜬다.
- **→ 에러·경고는 화면 안 인라인 UI(`Alert`, `Badge`, 빈 상태)로 표시한다.**
  layout에 Toaster를 추가하는 것은 전역 변경이라 이 작업 범위 밖이다(§9 결정 필요 4번).
- 기존 코드의 `alert()` 호출(`AuthPanel`, `OAuthRedirectHandler`)을 새 코드에 복사하지 않는다.

---

## 3. 아키텍처 결정

### 3.1 파일 배치

```text
nextjs/
├── app/ledger/page.tsx                        # 라우트 (서버 컴포넌트 껍데기)
├── components/ledger/
│   ├── ReceiptLedgerForm.tsx                  # "use client" — 폼 본체 + 이미지 미리보기
│   ├── ReceiptItemList.tsx                    # useFieldArray 품목 테이블
│   ├── ReceiptPreview.tsx                     # presigned 이미지 + 만료 대응
│   └── ReceiptLedgerSkeleton.tsx              # 로딩 스켈레톤
├── hooks/useAutoReceiptFetch.ts               # 페칭 + 상태 판별
└── lib/receiptApi.ts                          # 타입 + fetch 함수 + zod 스키마
```

`components/<페이지명>/` 규칙(`nextjs/CLAUDE.md`)을 따른다. `components/ui/`는 건드리지 않는다.

### 3.2 상태 모델

```ts
type ReceiptFetchState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; receipts: Receipt[]; hasMore: boolean; failures: ReceiptFailure[] }
  | { status: "error"; kind: ReceiptErrorKind; message: string };
```

`ReceiptErrorKind`는 `"unauthorized" | "forbidden" | "unavailable" | "network" | "unknown"`이다.
HTTP 상태를 화면이 직접 보지 않고, **`lib/receiptApi.ts`가 종류로 번역해서 올려 준다.**
컴포넌트에 `res.status === 401` 같은 분기를 두지 않는다.

`isLoading`/`error`/`data` 세 개의 독립 불리언을 만들지 않는다 — "로딩 중인데 에러도 있음" 같은
불가능한 조합이 생긴다. 판별 유니언 하나로 간다(`react_rules.md`의 "상태 객체로 묶는다"와 같은 취지).

### 3.3 자동 호출(Auto Trigger)의 함정

스펙 A항은 "Mount 시 API 호출"이다. 그대로 하면 두 가지 문제가 있다.

1. **React 19 개발 모드는 `useEffect`를 두 번 실행한다.** 이 API는 OCR 과금과 S3 이동을 일으킨다.
2. 사용자가 화면을 오갈 때마다 재호출된다.

백엔드는 멱등하므로(FAST-004 §3.3 — 이미 처리된 키는 OCR을 다시 타지 않는다) **데이터는 깨지지 않지만
네트워크 요청은 두 번 나간다.**

- **→ `useRef` 실행 락 + in-flight 가드로 마운트당 1회만 호출한다.**
- **→ `AbortController`로 언마운트 시 요청을 취소한다.** 언마운트 후 `setState`를 호출하지 않는다.
- 재조회는 **명시적인 [다시 불러오기] 버튼**으로만 한다. 폴링·자동 재시도를 넣지 않는다.

### 3.4 응답 계약 (백엔드 FAST-004 §3.6)

```jsonc
{
  "success": true,
  "data": {
    "receipts": [
      {
        "receiptId": "rcpt_12345678",
        "imageUrl": "https://...",      // presigned, TTL 10분
        "storeName": "클린카페 서울점",
        "transactionDate": "2026-08-04T10:00:00",
        "items": [{ "name": "아메리카노", "quantity": 2, "price": 9000 }],
        "totalAmount": 16500,
        "needsManualReview": false
      }
    ],
    "hasMore": false,
    "failures": []
  }
}
```

- `storeName` / `transactionDate` / `totalAmount`는 **`null`일 수 있다**(FAST-004 §3.5 파싱 실패 시).
  타입을 `string`으로 잡으면 런타임에 깨진다. `string | null`로 받고 폼에서 빈 값으로 채운다.
- `items`는 **빈 배열일 수 있다.**
- 응답은 외부 입력이므로 `unknown`으로 받아 **zod 스키마로 파싱**한다(`.claude/rules/typescript.md` §3).
  `as ReceiptResponse` 캐스팅으로 끝내지 않는다 — 백엔드가 `null`을 보낼 때 조용히 통과한다.

### 3.5 presigned URL 만료

`imageUrl`의 TTL은 10분이다(`RECEIPT_PRESIGN_TTL_SECONDS`). 사용자가 품목을 오래 고치면 이미지가 깨진다.

- **→ `<img onError>`로 만료를 감지해 "이미지 링크가 만료되었습니다 · [다시 불러오기]" 플레이스홀더를 띄운다.**
- 이미지가 깨져도 **입력 중이던 폼 값은 절대 버리지 않는다.** 재조회는 사용자가 누를 때만 한다.
- `next/image`를 쓰지 않는다. `next.config.mjs`가 `images.unoptimized: true`이고 presigned URL은
  `remotePatterns` 등록이 필요해 이득이 없다. 기존 코드도 `<img>`를 쓴다.

### 3.6 엣지 케이스 → UI 매핑

스펙 5번의 "엣지 케이스 처리"를 아래 표로 고정한다. 이 표가 §7 회귀 시나리오의 기준이다.

| 상태 | UI | 사용 컴포넌트 |
|------|-----|---------------|
| `loading` | 이미지 자리 + 폼 필드 형태의 스켈레톤 | `ui/skeleton` |
| 영수증 0장 | "새로 인식할 영수증이 없습니다" + 업로드 안내 | `ui/empty` |
| `401` | "로그인이 필요합니다" + `/login` 링크 | `ui/alert` + `next/link` |
| `403` | "이 기능을 사용할 권한이 없습니다" | `ui/alert` |
| `503` | "영수증 저장소가 준비되지 않았습니다. 잠시 후 다시 시도해 주세요." | `ui/alert` |
| 네트워크 실패 | "서버에 연결할 수 없습니다" + [다시 시도] | `ui/alert` + `ui/button` |
| `failures[]` 비어있지 않음 | "N장은 읽지 못했습니다" 경고 배너 (성공분은 그대로 표시) | `ui/alert` |
| `needsManualReview: true` | 카드 상단에 "확인이 필요한 항목이 있습니다" 배지 | `ui/badge` |
| 누락 필드(`null`) | 해당 입력에 개별 표시 + 포커스 유도 | `ui/badge` |
| `hasMore: true` | 목록 하단 [더 불러오기] | `ui/button` |
| 이미지 만료 | §3.5 플레이스홀더 | — |

- 에러 문구는 전부 **한국어**로 쓰고, 백엔드 `detail` 원문이나 스택트레이스를 그대로 노출하지 않는다.
- **부분 성공을 실패로 취급하지 않는다.** `failures`가 있어도 `receipts`가 있으면 폼을 띄운다.

### 3.7 검산 표시

FAST-004 §3.5에 따라 파서는 총액을 임의로 보정하지 않는다. 프론트도 마찬가지다.

- `sum(items.price) !== totalAmount`면 합계 옆에 **차액을 안내만** 하고 값을 자동으로 덮어쓰지 않는다.
- 사용자가 [합계로 맞추기]를 누를 때만 반영한다.
- 금액은 **원 단위 정수**다. `parseFloat`·부동소수 연산을 쓰지 않는다.

---

## 4. 제약

- 새 런타임 의존성을 추가하지 않는다(TanStack Query·Formik·날짜 라이브러리 포함). §9 결정 전까지.
- `components/ui/`는 수정하지 않는다. 필요한 shadcn 컴포넌트는 이미 전부 있다.
- `.claude/rules/typescript.md` 준수 — `type` 우선, `any` 금지, Props는 `<컴포넌트명>Props`,
  named export, 상수는 `as const`.
- 기존 파일 수정은 **최소**로: `app/ledger/page.tsx` 신규 + 사이드바/네비 링크 1줄.
  다른 화면의 폼·페칭 코드를 "개선"하지 않는다.
- `alert()`를 쓰지 않는다(§2.9).
- 클라이언트 컴포넌트 경계를 좁게 잡는다. `"use client"`를 `app/ledger/page.tsx` 최상단에 걸어
  페이지 전체를 클라이언트로 만들지 않는다.
- 토큰을 URL 쿼리·로그·에러 메시지에 절대 넣지 않는다.
- 영수증 이미지·금액을 `console.log`로 남기지 않는다(개인 결제 정보다).

---

## 5. 작업 순서

각 단계 완료 후 변경 요약을 출력하고 검증을 통과시킨 뒤 다음으로 간다.

### 5.0 액세스 토큰 확보 경로 (코드보다 먼저)

§2.4의 블로킹 이슈다. **여기가 정해지기 전에는 §5.4 이후로 넘어가지 않는다.**

정해야 할 것: 로그인 성공 시 토큰을 어디에 두고, 요청 시 누가 헤더에 싣는가.

- 최소안: `lib/receiptApi.ts`가 토큰 획득 함수 하나(`getAccessToken()`)에만 의존하게 만들고,
  그 함수의 구현은 별도 작업으로 분리한다. **이 화면 안에 로그인 로직을 만들지 않는다.**
- 개발 중에는 `getAccessToken()`이 `null`을 반환해도 화면이 401 UI로 정상 동작해야 한다.

**검증:** 토큰 없이 `/ledger` 진입 → 흰 화면·콘솔 에러 없이 "로그인이 필요합니다" 안내가 뜬다.

### 5.1 타입 + zod 스키마

`lib/receiptApi.ts`에 §3.4 응답 계약을 `type` + zod 스키마로 선언한다.
`storeName` / `transactionDate` / `totalAmount`는 **nullable**이다.

**검증:** `pnpm exec tsc --noEmit` 통과. `null`이 섞인 페이크 응답을 스키마에 통과시켜
`storeName: null`이 그대로 살아 있는지 확인(캐스팅으로 뭉개지지 않았는지).

### 5.2 API 계층

`lib/receiptApi.ts` — `fetchAutoProcessedReceipts(signal): Promise<ReceiptFetchResult>`.

- `POST ${API_BASE}/api/dumb-and-dumber/receipts/auto-process`
- `Authorization: Bearer` 헤더(§5.0)
- `API_BASE`는 기존 관례를 따른다:
  `process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000"`
- HTTP 상태 → `ReceiptErrorKind` 번역(§3.2)

**검증:** 401/403/503/네트워크 단절 각각에 대해 올바른 `kind`가 나온다. 이 함수는 예외를 던지지 않고
결과 객체로 돌려준다(`try/catch`가 컴포넌트로 새지 않게).

### 5.3 커스텀 훅

`hooks/useAutoReceiptFetch.ts` — §3.2 상태 + §3.3 가드(`useRef` 락 · `AbortController`) + `refetch()`.

**검증:**

| 케이스 | 기대 |
|--------|------|
| 개발 모드 마운트 | 네트워크 요청 **1회** (Network 탭에서 확인) |
| 즉시 언마운트 | 요청 abort, "unmounted component" 경고 없음 |
| `refetch()` 연타 | in-flight 중이면 무시, 중복 요청 없음 |

### 5.4 프레젠테이션 컴포넌트

- `ReceiptLedgerSkeleton.tsx` — 이미지 + 필드 형태의 스켈레톤.
- `ReceiptPreview.tsx` — `<img>` + §3.5 만료 처리.
- `ReceiptItemList.tsx` — `useFieldArray` 기반 품목 테이블(`ui/table`), 행 추가·삭제.
- `ReceiptLedgerForm.tsx` — `useForm` + `zodResolver`, 위 셋을 조립, 배지·경고 배너(§3.6).

**검증:** 페이크 데이터로 각 상태를 눈으로 확인한다.

| 케이스 | 기대 |
|--------|------|
| 품목 3행에서 2행 삭제 | 남은 행 값이 밀리지 않고 유지 |
| 행 추가 | 빈 행 추가, 합계 안내 갱신 |
| 수량 0 / 음수 | zod 검증 실패 메시지 (한국어) |
| `storeName: null` | 빈 입력 + 확인 필요 배지 |
| `needsManualReview: true` | 카드 상단 배지 노출 |
| `sum !== totalAmount` | 차액 안내, **값 자동 변경 없음** |
| 라이트/다크 토글 | 두 테마 모두 대비 정상 |

### 5.5 페이지 조립

`app/ledger/page.tsx` — 훅 + 컴포넌트 결합, §3.6 상태 매핑 전체.
좌측 사이드바(`components/layout/LeftSidebar.tsx`)에 `/ledger` 링크 1줄 추가.

**검증:** §7 시나리오 전체.

### 5.6 저장 버튼

§2.3에 따라 **백엔드 엔드포인트가 없다.** §9 결정 3번이 정해지기 전까지:

- 버튼은 렌더링하되 `disabled`로 두고 "저장 API 준비 중" 안내를 단다.
- **또는** 폼 값을 `console` 없이 상위 콜백으로만 넘기고 실제 호출은 비워 둔다.

없는 엔드포인트를 호출하는 코드를 미리 써 두지 않는다 — 404를 내는 죽은 코드가 된다.

### 5.7 최종 검증

```bash
cd nextjs
pnpm exec tsc --noEmit
pnpm build
```

---

## 6. 완료 기준

- [ ] `/ledger` 진입 시 스켈레톤 → 결과 폼으로 전환된다.
- [ ] 개발 모드에서도 자동 호출이 **정확히 1회**다.
- [ ] 401 / 403 / 503 / 네트워크 실패 / 영수증 0장 / 부분 실패가 각각 **다른 한국어 안내**로 표시된다.
- [ ] 백엔드 `detail` 원문·스택트레이스·토큰이 화면과 콘솔에 노출되지 않는다.
- [ ] `storeName`·`transactionDate`·`totalAmount`가 `null`이어도 렌더링이 깨지지 않는다.
- [ ] 품목 행 추가·삭제 시 다른 행의 값이 밀리지 않는다.
- [ ] `needsManualReview: true`에 배지가 뜬다.
- [ ] 합계 불일치를 **안내만** 하고 값을 자동으로 덮어쓰지 않는다.
- [ ] 라이트/다크 모드 양쪽에서 대비가 정상이다.
- [ ] presigned URL 만료 시 폼 입력값을 잃지 않는다.
- [ ] `any` 없음, `type` 사용, named export, Props 타입 명명 규칙 준수.
- [ ] 새 런타임 의존성이 추가되지 않았다(`package.json` diff 없음).
- [ ] `pnpm exec tsc --noEmit`과 `pnpm build`가 모두 통과한다.

---

## 7. 회귀 시나리오

| # | 시나리오 | 기대 |
|---|----------|------|
| 1 | 토큰 없이 `/ledger` 진입 | 401 안내 + 로그인 링크. 흰 화면·콘솔 에러 없음 |
| 2 | 영수증 2장 상태로 진입 | 스켈레톤 → 2개 카드. 요청 1회 |
| 3 | 진입 직후 즉시 뒤로가기 | 요청 abort, React 경고 없음 |
| 4 | 백엔드 중지 상태로 진입 | "서버에 연결할 수 없습니다" + [다시 시도] |
| 5 | 3장 중 1장 OCR 실패(`failures` 1건) | 2장 정상 표시 **+** 경고 배너. 전체 실패로 처리하지 않음 |
| 6 | 총액만 `null`인 영수증 | 총액 입력 비어 있고 확인 필요 배지, 나머지 필드는 정상 |
| 7 | 품목 3행 중 2행 삭제 후 1행 추가 | 남은 값 유지, 새 행은 빈 값 |
| 8 | 폼을 11분간 열어 둔 뒤 이미지 확인 | 이미지 만료 플레이스홀더, **입력값 보존** |
| 9 | `hasMore: true`에서 [더 불러오기] | 추가분이 목록에 append, 기존 편집값 유지 |
| 10 | 다크 모드 토글 | 배지·경고·테이블 대비 정상 |

nextjs에는 테스트 하네스가 없다(루트 CLAUDE.md). 위 시나리오는 **수동 확인**이며,
백엔드는 `RECEIPT_OCR_PROVIDER=fake`로 띄워 외부 OCR 과금 없이 재현한다(FAST-004 §5.1).

---

## 8. 범위 밖

- **로그인·토큰 저장·갱신 플로우 구현**(§5.0에서 인터페이스만 정한다).
- 가계부 저장 API 연동 — 백엔드 엔드포인트가 없다(§2.3).
- 영수증 **업로드** UI. 이 화면은 이미 S3에 올라온 파일만 다룬다.
- 카테고리 분류, 월별 집계, 예산 등 가계부 본체 화면.
- eslint 설치·설정(§2.5), layout에 `<Toaster />` 마운트(§2.9).
- 기존 화면의 페칭·폼 코드 리팩터링.
- `nextjs/CLAUDE.md`의 `pnpm lint` 안내 수정 — 사실만 §2.5에 기록한다.

---

## 9. 가정 / 결정 필요

**가정(그대로 진행)**

- 라우트는 `/ledger`, 컴포넌트는 `components/ledger/`. 백엔드의 영화 캐릭터 네이밍을 프론트로 옮기지 않는다.
- 인증은 `Authorization: Bearer` 헤더(§2.4). 쿠키 경로는 도메인이 달라 쓸 수 없다.
- 새 의존성 없이 `useState` + `fetch` + 이미 설치된 RHF/zod로 구현한다.
- `transactionDate`는 `<Input type="datetime-local">`로 받는다.
- 금액은 원 단위 정수, KRW 고정.

**결정 필요 (착수 전 확인)**

1. **TanStack Query를 도입할 것인가.** 이 화면 하나에는 과하다고 보고 넣지 않았다.
   앞으로 서버 상태를 쓰는 화면이 여럿 생길 계획이면 지금 넣는 편이 싸다.
2. **토큰 보관 위치** — `localStorage`(XSS 노출) vs 메모리 + 리프레시(복잡·새로고침 시 재로그인).
   `api.ragtaylor.com`과 `auth.ragtailor.com`이 다른 등록 도메인이라 httpOnly 쿠키는 후보에서 빠진다.
   이건 이 화면보다 큰 결정이라 별건으로 정하는 편이 낫다.
3. **저장 API(`POST .../entries`)를 백엔드 범위에 넣을 것인가.** 넣지 않으면 이 화면은
   "인식 결과 확인"까지만 완결된다(§5.6).
4. **layout에 `<Toaster />`를 마운트할 것인가.** 마운트하면 전역 컴포넌트가 하나 늘지만
   이후 모든 화면이 토스트를 쓸 수 있다. 이번엔 인라인 UI로 우회했다.
5. **`NEXT_PUBLIC_API_URL` vs `NEXT_PUBLIC_API_BASE_URL`** — 두 변수가 같은 값을 가리키며 혼용된다
   (`.env.example`에 둘 다 있다). 이번엔 인증이 필요한 컴포넌트들이 쓰는 `NEXT_PUBLIC_API_BASE_URL`을
   따랐다. 통일 여부는 별건.
6. **`/ledger` 진입점을 어디에 노출할 것인가** — 좌측 사이드바 / 상단바 / `/dashboard` 카드.
   §5.5는 사이드바를 가정했다.
