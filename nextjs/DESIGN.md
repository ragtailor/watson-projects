# DESIGN.md — 프론트엔드 스타일링 하네스

`nextjs/`의 스타일링 규칙과 그것을 강제하는 하네스를 정의한다.
루트 지침은 [../CLAUDE.md](../CLAUDE.md), 프론트엔드 일반 지침은 [CLAUDE.md](CLAUDE.md)를 참고한다.

- 기준일: 2026-08-04
- 강제 도구: [`scripts/validate-design.mjs`](scripts/validate-design.mjs) — `pnpm design:check`
- 이 문서와 검증 스크립트가 어긋나면 **스크립트가 사실이다.** 문서를 고친다.

---

## 0. 왜 이 문서가 있나

`fastapi/`는 `import-linter` · `markdownlint` · `validate_harness.py`로 구조 무결성을 자동 강제한다.
프론트엔드에는 그런 하네스가 없었고, 그 결과 **디자인 토큰 체계와 하드코딩된 색상값이 병존**했다.

- `app/globals.css`에 shadcn 토큰(`--background`, `--card`, `--muted` …)이 정의돼 있는데,
  실제 화면 컴포넌트는 `dark:bg-[#111111]` 같은 **매직 hex를 24개 파일에 65번** 박아 쓰고 있었다.
- `styles/globals.css`가 `app/globals.css`의 사본으로 남아 있었고 **어디서도 임포트되지 않았다.**
  유일한 고유 내용(`.marquee`, `@keyframes marquee-right`)도 쓰이는 곳이 없었다.

같은 색을 두 방식으로 표현하면 테마를 바꿀 때 한쪽만 바뀐다. 이 문서는 그 분기를 없애고,
다시 갈라지지 않도록 검증으로 묶는다.

---

## 1. 단일 스타일링 체계

**Tailwind CSS v4 + shadcn/ui.** 이 둘 외의 스타일링 수단을 쓰지 않는다.

| 수단 | 사용 여부 | 비고 |
|------|-----------|------|
| Tailwind 유틸리티 클래스 | ✅ 기본 | |
| shadcn/ui 컴포넌트 (`components/ui/`) | ✅ 기본 | `pnpm dlx shadcn@latest add <component>`로만 갱신 |
| `app/globals.css`의 CSS 변수(토큰) | ✅ | 색·반경의 **단일 출처** |
| `cn()` (`lib/utils.ts`) | ✅ | 조건부 클래스 병합 |
| CVA (`class-variance-authority`) | ✅ | shadcn 컴포넌트 내부 관례 |
| styled-components / emotion | ❌ | 규칙 3이 차단 |
| CSS Modules (`*.module.css`) | ❌ | 규칙 3이 차단 |
| 추가 전역 CSS 파일 | ❌ | 규칙 2가 차단 |
| Tailwind 임의 색상값 `[#…]` | ❌ | 규칙 1이 차단 |
| 인라인 `style`의 색상 리터럴 | ❌ | 규칙 4가 차단 |

> Tailwind v4는 **CSS-first 설정**이다. `tailwind.config.*` 파일이 없는 것은 정상이며,
> 만들지 않는다. 테마 확장은 `app/globals.css`의 `@theme inline` 블록에서 한다.
> PostCSS 플러그인은 `@tailwindcss/postcss` 하나다(`postcss.config.mjs`).

**인라인 `style`은 색이 아닌 동적 수치에만 허용된다.** 현재 저장소의 3건이 그 예다 —
`animationDelay`, `transform: translateX(...)`, 차트 런타임 값. 색은 언제나 className으로 표현한다.

---

## 2. 디자인 토큰

### 2.1 단일 출처

**`app/globals.css`가 유일한 토큰 정의 파일이다.** 구조는 세 블록이다.

```text
:root { … }          라이트 모드 값
.dark { … }          다크 모드 오버라이드
@theme inline { … }  Tailwind 유틸리티로 노출 (--color-* → bg-*, text-*, border-* …)
```

`@theme inline`에 등록해야 `bg-surface` 같은 유틸리티가 생성된다.
`:root`/`.dark`에만 추가하고 `@theme inline`을 빼먹으면 **클래스가 조용히 무시된다.**

다크 모드 변형은 `@custom-variant dark (&:is(.dark *))`로 정의돼 있고,
`next-themes`가 `<html>`에 `.dark`를 붙인다(`app/layout.tsx`).

### 2.2 토큰 목록

shadcn 기본 토큰(`--background`, `--foreground`, `--card`, `--popover`, `--primary`,
`--secondary`, `--muted`, `--accent`, `--destructive`, `--border`, `--input`, `--ring`,
`--chart-1..5`, `--sidebar-*`, `--radius`)은 shadcn이 관리한다. **값을 임의로 바꾸지 않는다** —
바꾸면 55개 UI 컴포넌트의 외형이 한꺼번에 움직인다.

이 프로젝트가 추가한 토큰은 아래 여섯 개다.

| 토큰 | 유틸리티 | 라이트 | 다크 | 용도 |
|------|----------|--------|------|------|
| `--surface` | `bg-surface` | `#ffffff` | `#111111` | 카드·패널·팝업 표면 |
| `--surface-muted` | `bg-surface-muted` | `#f5f5f5` | `#1a1a1a` | 입력창·탭 트랙 등 눌린 표면 |
| `--surface-hover` | `bg-surface-hover` | `#e5e5e5` | `#222222` | 표면 위 hover 상태 |
| `--brand-kakao` | `bg-brand-kakao` | `#fee500` | 동일 | 카카오 로그인 버튼 |
| `--brand-kakao-foreground` | `fill-brand-kakao-foreground` | `#391b1b` | 동일 | 카카오 로고 |
| `--brand-naver` | `bg-brand-naver` | `#03c75a` | 동일 | 네이버 로그인 버튼 |

**페이지 배경은 새 토큰을 만들지 않았다.** 기존 `--background`의 다크 값
`oklch(0.145 0 0)`이 하드코딩돼 있던 `#0a0a0a`와 **정확히 같아서**(oklch 왕복 변환으로 확인)
`dark:bg-background`를 그대로 쓴다.

### 2.3 색 표기 규칙

- 회색조·UI 색은 **oklch**로 쓴다(기존 shadcn 블록과 통일). 다크 표면 값은 마이그레이션 전
  hex와 정확히 일치하도록 계산해 넣었다: `oklch(0.178 0 0)=#111111`,
  `oklch(0.218 0 0)=#1a1a1a`, `oklch(0.252 0 0)=#222222`.
- **브랜드 색은 hex 원문을 유지한다.** 외부 브랜드 가이드가 값을 지정하고,
  oklch 3자리로는 왕복이 정확하지 않다(`#03c75a` → oklch → `#06c75a`).
  브랜드 색은 "비슷한 색"이면 안 되므로 변환하지 않는다.

---

## 3. 클래스 작성 규칙

### 3.1 색은 반드시 토큰 또는 Tailwind 팔레트로

```tsx
// ❌ 매직 hex — 어디서 온 값인지 알 수 없고 테마 전환에서 누락된다
<div className="bg-white dark:bg-[#111111]" />

// ✅ 토큰
<div className="bg-white dark:bg-surface" />
```

Tailwind 기본 팔레트(`neutral-400`, `sky-600`, `gray-700` …)는 **허용된다.**
Tailwind의 일부이므로 통일 대상이 아니다. 금지되는 것은 `[#…]` 같은 **임의 값**이다.

새 색이 필요하면 §6의 절차를 따른다. 임의 값으로 먼저 넣고 나중에 정리하지 않는다.

### 3.2 라이트/다크 쌍을 함께 쓴다

배경·테두리·텍스트 색을 지정할 때 다크 대응을 같은 자리에 적는다.
`_docs/darkmode-spec.md`의 방침(기본 라이트, 토글 제공)을 따른다.

현재 저장소의 관용 조합:

| 역할 | 클래스 |
|------|--------|
| 페이지 배경 | `bg-white dark:bg-background` |
| 카드·패널 | `bg-white dark:bg-surface` |
| 입력·탭 트랙 | `bg-slate-50/50 dark:bg-surface-muted` |
| 테두리 | `border-slate-200 dark:border-gray-700` |
| 본문 텍스트 | `text-neutral-900 dark:text-neutral-100` |
| 보조 텍스트 | `text-neutral-500 dark:text-neutral-400` |
| 강조(브랜드) | `text-sky-600 dark:text-sky-400` |

### 3.3 shadcn 컴포넌트

- `components/ui/`는 **직접 수정하지 않는다.** 생성기 출력이 우선이며 우리 규칙보다 앞선다.
- 외형 조정은 호출부에서 `className` + `cn()`으로 한다.
- 필요한 컴포넌트는 이미 55개 있다. 새 원시 컴포넌트를 손으로 만들기 전에
  `components/ui/`를 먼저 확인한다.

### 3.4 투명도·상태 변형

토큰은 Tailwind 색으로 등록돼 있으므로 수식어가 그대로 붙는다. 별도 토큰을 만들지 않는다.

```tsx
dark:bg-surface/50                      // color-mix로 컴파일됨
dark:hover:bg-surface-hover
dark:data-[state=active]:bg-surface
```

---

## 4. 하네스 (자동 검증)

```bash
cd nextjs
pnpm design:check   # 디자인 하네스 — 이 문서의 규칙
pnpm typecheck      # tsc --noEmit
pnpm build          # 빌드
```

`scripts/validate-design.mjs`가 강제하는 규칙:

| # | 규칙 | 위반 예 |
|---|------|---------|
| 1 | Tailwind 임의 색상값 금지 | `bg-[#111111]`, `text-[rgb(0,0,0)]` |
| 2 | 전역 CSS는 `app/globals.css` 하나 | `styles/globals.css` 추가 |
| 3 | Tailwind/shadcn 외 스타일링 라이브러리 금지 | `import styled from "styled-components"` |
| 4 | 인라인 `style`의 색상 리터럴 금지 | `style={{ color: "#333" }}` |

추가로 브랜드 토큰 3종이 `app/globals.css`에 존재하는지 확인한다.

### 4.1 `pnpm lint`는 동작하지 않는다

`package.json`에 `"lint": "eslint ."`가 있지만 **eslint가 의존성에도 `node_modules/.bin`에도 없고
설정 파일도 없다.** 실행하면 exit code 2로 실패한다.

더해 `next.config.mjs`의 `typescript.ignoreBuildErrors: true` 때문에
**`pnpm build`는 타입 에러를 잡지 않는다.** 그래서 `pnpm typecheck`를 별도 스크립트로 추가했다.

검증은 위 세 명령을 모두 돌린다. eslint 설치는 별건이다(§7).

---

## 5. 이번 통일 작업에서 실제로 바뀐 것

시각적 변화 없이 표현만 통일하는 것이 목표였다. 다크 표면 값이 마이그레이션 전 hex와
정확히 같도록 계산해 넣었고, 빌드 산출 CSS에서 `.dark{--surface:#111}` 등으로 확인했다.

**토큰 추가** — `app/globals.css`에 `--surface` / `--surface-muted` / `--surface-hover` /
브랜드 3종을 `:root` · `.dark` · `@theme inline` 세 곳에 등록.

**치환** — 24개 파일 65건.

| 이전 | 이후 | 건수 |
|------|------|------|
| `dark:bg-[#1a1a1a]` | `dark:bg-surface-muted` | 24 |
| `dark:bg-[#111111]` | `dark:bg-surface` | 21 |
| `dark:bg-[#0a0a0a]` | `dark:bg-background` | 12 |
| `dark:bg-[#111111]/50` | `dark:bg-surface/50` | 2 |
| `dark:data-[state=active]:bg-[#111111]` | `dark:data-[state=active]:bg-surface` | 2 |
| `dark:hover:bg-[#222]` | `dark:hover:bg-surface-hover` | 1 |
| `bg-[#FEE500]` / `fill-[#391B1B]` / `bg-[#03C75A]` | `bg-brand-kakao` / `fill-brand-kakao-foreground` / `bg-brand-naver` | 3 |

**삭제** — `styles/globals.css`. 임포트되는 곳이 없었고, 고유 내용인 `.marquee` /
`@keyframes marquee-right`도 사용처가 없었다(전 소스 검색 0건).

**추가** — `scripts/validate-design.mjs`, `package.json`의 `design:check` · `typecheck` 스크립트.

검증 결과: `pnpm design:check` 통과(소스 128개), `pnpm typecheck` 통과, `pnpm build` 통과.

> 시각 회귀 테스트 하네스는 없다(루트 CLAUDE.md — nextjs에는 테스트가 없다).
> 값 동일성은 산출 CSS 확인으로 검증했으나, **화면 확인은 수동이다.**
> 다크 모드로 `/`, `/login`, `/notice`, `/dashboard`, `/lesson/titanic`을 한 번 훑어보길 권한다.

---

## 6. 새 색이 필요할 때

1. 기존 토큰이나 Tailwind 팔레트로 되는지 먼저 확인한다. 대부분 된다.
2. 정말 새 토큰이 필요하면 `app/globals.css`의 **세 곳 모두**에 추가한다.
   - `:root` — 라이트 값
   - `.dark` — 다크 값
   - `@theme inline` — `--color-<이름>: var(--<이름>);`
3. 이 문서 §2.2 표에 행을 추가한다.
4. `pnpm design:check && pnpm typecheck && pnpm build`.

한 화면에서만 쓰는 색을 위해 토큰을 만들지 않는다. 토큰은 **재사용되는 의미**에만 붙인다.

---

## 7. 범위 밖 (알려진 미해결)

- **eslint 설치·설정** — `pnpm lint`가 실패하는 상태 그대로다. Tailwind 클래스 정렬
  (`prettier-plugin-tailwindcss`)도 도입하지 않았다.
- **시각 회귀 테스트** — 스냅샷/Storybook 없음. §5의 수동 확인 목록으로 대신한다.
- **`dark:` 유틸리티의 토큰화** — `dark:text-neutral-100`(55회), `dark:border-gray-700`(48회) 등
  Tailwind 팔레트 직접 사용은 그대로 뒀다. Tailwind의 일부이므로 규칙 위반이 아니며,
  의미 토큰(`text-muted-foreground` 등)으로 옮기는 것은 외형이 실제로 바뀌는 별개 작업이다.
- **shadcn 기본 토큰과 앱 표면값의 이원화** — `--card`(다크 `#0a0a0a`)와 `--surface`(`#111111`)가
  다른 값이다. shadcn `Card`와 손으로 만든 패널의 배경이 미세하게 다르다.
  통일하려면 `--card` 값을 바꿔야 하는데 55개 컴포넌트에 영향이 가므로 별건으로 판단한다.
