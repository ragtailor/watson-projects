---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript 규칙

`nextjs/`에서 실제로 쓰이고 있는 패턴을 기준으로 한다. 새 코드는 아래를 따르고,
기존 파일을 수정할 때는 그 파일의 스타일을 우선한다 (루트 CLAUDE.md §3 정밀한 수정).

---

## 1. 기본

- **strict mode 필수.** `nextjs/tsconfig.json`의 `"strict": true`를 끄지 않는다.
- **`any` 금지.** 외부에서 들어온 값은 `unknown`으로 받고 좁혀서 쓴다.
- **인터페이스보다 타입 별칭(`type`)을 선호한다.**
- `enum`을 쓰지 않는다. 유니언 리터럴 또는 `as const` 객체로 대체한다.

`next.config.mjs`의 `typescript.ignoreBuildErrors: true`는 의도된 설정이지만,
**타입 에러를 방치해도 된다는 뜻은 아니다.** 빌드가 통과해도 타입은 맞춰 놓는다.

---

## 2. 타입 별칭 우선

선언은 `type`을 기본으로 한다. 유니언·교차·매핑·`typeof` 파생 등 실제 쓰이는
표현을 그대로 담을 수 있다.

```ts
// components/GeminiHeroChat.tsx
type Role = "user" | "assistant";
type ChatMessage = { id: string; role: Role; text: string };
```

```ts
// components/ui/toast.tsx — 라이브러리 타입에서 파생
type ToastProps = React.ComponentPropsWithoutRef<typeof Toast>;
```

`interface`는 `lib/`의 순수 데이터 모델처럼 이미 그렇게 선언된 곳에서만 유지한다
(`lib/crawlingBoard.ts`의 `BoardPost`). 새로 만드는 타입은 `type`으로 쓴다.
선언 병합(declaration merging)이 필요한 경우에만 `interface`가 정당한 선택이다.

---

## 3. `unknown` 우선, `any` 금지

파싱된 JSON, API 응답, 에러 객체는 `unknown`으로 받고 `typeof` / `in` /
`Array.isArray`로 좁힌다.

```ts
// app/api/gemini/chat/route.ts
function extractGeminiError(raw: string, parsed: unknown) {
  if (typeof parsed === "object" && parsed !== null) {
    const body = parsed as Record<string, unknown>;
    const apiError = body.error ?? body.message;
    if (typeof apiError === "string") return apiError;
    // ...
  }
  return raw || "Gemini API 오류";
}
```

에러는 `instanceof`로 좁힌다.

```ts
const msg = e instanceof Error ? e.message : "알 수 없는 오류";
```

`fetch` 응답은 기대 형태를 명시해 받는다.

```ts
const data = (await res.json()) as { text?: string; detail?: unknown };
```

> **현재 남아 있는 예외:** `components/GeminiHeroChat.tsx`,
> `components/moneyball/MoneyballHeroChat.tsx`, `app/api/gemini/chat/route.ts`의
> `parseApiError` / `extractGeminiError`에 `as any`가 남아 있다. 새 코드에서
> 복사하지 않는다. 해당 파일을 손볼 일이 생기면 `Record<string, unknown>` 캐스팅
> 뒤 `typeof` 검사로 정리한다.

---

## 4. 컴포넌트 Props

- Props는 `<컴포넌트명>Props` 이름의 `type`으로 선언한다.
- 컴포넌트는 **named export** 함수 선언을 기본으로 한다 (`export function Xxx`).
- 선택 값은 `?`와 기본값으로 처리하고, `className?: string`을 받아 `cn()`으로 합친다.

```tsx
// components/home/PortfolioItem.tsx
import { cn } from "@/lib/utils";
import type { PortfolioItemData } from "./portfolio-data";

type PortfolioItemProps = {
  item: PortfolioItemData;
  featured?: boolean;
  className?: string;
};

export function PortfolioItem({
  item,
  featured = false,
  className,
}: PortfolioItemProps) {
  return <article className={cn("group flex flex-col", className)}>...</article>;
}
```

콜백 Props는 `on*` 이름에 반환 타입까지 적는다.

```ts
// components/layout/MobileMenu.tsx
type MobileMenuProps = {
  onClose: () => void;
  shopOpen: boolean;
  onToggleShop: () => void;
  isLessonPage?: boolean;
};
```

`components/ui/`(shadcn 자동 생성)는 직접 수정하지 않는다. 그쪽은 DOM 속성을
`React.ComponentProps<'button'> & VariantProps<typeof buttonVariants>`처럼
확장하는 shadcn 관례를 따르며, 우리 규칙보다 생성기 출력이 우선이다.

---

## 5. 상수는 `as const`, 타입은 거기서 파생

값과 타입을 두 번 적지 않는다. 상수 배열/객체에 `as const`를 붙이고 타입을 뽑아 쓴다.

```tsx
// components/GeminiHeroChat.tsx
const MODEL_OPTIONS = [
  { key: "fast", label: "빠른 응답" },
  { key: "pro", label: "고품질" },
] as const;

const [modelKey, setModelKey] =
  useState<(typeof MODEL_OPTIONS)[number]["key"]>("fast");
```

키가 고정된 조회 테이블은 `Record`로 명시한다.

```ts
// app/api/gemini/chat/route.ts
const MODEL_IDS: Record<string, string> = {
  fast: "gemini-2.5-flash",
  pro: "gemini-2.5-pro",
};
```

---

## 6. 훅 타이핑

- `useState`는 초기값으로 추론되지 않을 때만 제네릭을 붙인다.
  - `useState("")` → 제네릭 불필요
  - `useState<ChatMessage[]>([])`, `useState<string | null>(null)` → 필요
- `useRef`는 DOM 엘리먼트 타입을 명시한다: `useRef<HTMLTextAreaElement>(null)`.
- Context는 값 타입을 `type`으로 선언하고 `createContext<T>`에 넘긴다.

```tsx
// components/layout/RightPanelContext.tsx
type Ctx = {
  content: ReactNode;
  setContent: (node: ReactNode) => void;
};

const RightPanelContext = createContext<Ctx>({
  content: null,
  setContent: () => {},
});
```

---

## 7. Route Handler (`app/api/**/route.ts`)

- 시그니처는 `NextRequest` / `NextResponse`를 쓴다.
- 요청 본문은 **파싱 전에 기대 형태를 선언**하고, `req.json()` 실패를 잡는다.
- 응답은 성공 `{ ... }` / 실패 `{ error: string }` + 적절한 `status`로 통일한다.

```ts
export async function POST(req: NextRequest) {
  let body: { messages?: ChatMessage[]; modelKey?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "잘못된 요청 본문입니다." }, { status: 400 });
  }
  // ...
}
```

에러 메시지는 사용자에게 노출되므로 **한국어**로 쓰고, 상위 API 키·URL 등
내부 정보를 그대로 흘리지 않는다.

---

## 8. import

- 타입 전용 import는 `import type` 또는 인라인 `type` 지정자를 쓴다.
  `isolatedModules: true`이므로 이 구분이 필요하다.

```ts
import { clsx, type ClassValue } from "clsx";
import type { PortfolioItemData } from "./portfolio-data";
```

- 프로젝트 내부 참조는 경로 별칭 `@/`를 쓴다 (`@/lib/utils`, `@/components/ui/button`).
  같은 디렉터리 내부 참조에만 상대 경로를 허용한다.
- 클라이언트 컴포넌트는 파일 최상단에 `"use client";`를 둔다. 상태·이벤트·브라우저
  API가 필요 없으면 붙이지 않는다 (App Router 기본은 서버 컴포넌트).

---

## 9. 브라우저 전용 코드

`localStorage` 등은 서버 렌더링에서 실행될 수 있으므로 가드한다.

```ts
// lib/crawlingBoard.ts
function getStoredPosts(): BoardPost[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as BoardPost[]) : [];
  } catch {
    return [];
  }
}
```

---

## 10. 체크리스트

새 `.ts` / `.tsx` 파일을 추가하거나 수정했다면:

- [ ] `any`가 없다 (`unknown` + 좁히기로 해결했다)
- [ ] 새 타입은 `type` 별칭으로 선언했다
- [ ] Props 타입 이름이 `<컴포넌트명>Props`다
- [ ] 상수 리터럴에 `as const`를 붙이고 타입을 파생시켰다
- [ ] 타입 전용 import에 `type` 지정자를 붙였다
- [ ] 내부 import가 `@/` 별칭을 쓴다
- [ ] `pnpm build`가 통과한다 (`ignoreBuildErrors`에 기대지 않는다)
