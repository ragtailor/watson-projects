# Frontend — taylor

Next.js TypeScript 프론트엔드. 루트 지침은 [../CLAUDE.md](../CLAUDE.md)를 참고한다.

---

## 실행

```bash
cd taylor
pnpm dev        # 개발 서버 (localhost:3000)
pnpm build      # 프로덕션 빌드
pnpm lint       # ESLint
```

패키지 매니저는 **pnpm**을 사용한다. `npm install` 또는 `yarn`은 사용하지 않는다.

---

## 환경 변수

`taylor/.env.local`:

```
GEMINI_API_KEY=...
NEXT_PUBLIC_API_URL=http://localhost:8000   # tailor 백엔드
```

---

## 기술 스택

- **Next.js 16** (App Router) + **React 19** + **TypeScript 5.7**
- **Tailwind CSS v4** (`@tailwindcss/postcss`)
- **shadcn/ui** — `components/ui/`에 Radix UI 기반 컴포넌트
  - 새 UI 컴포넌트: `pnpm dlx shadcn@latest add <component>`
- **Gemini AI** — `app/api/gemini/chat/route.ts`가 Google REST API 직접 호출 (SDK 미사용)
- **Vercel Blob** — 파일 업로드 저장소

DB는 온프레미스(api.ragtaylor.com)에만 존재하며, nextjs는 직접 접근하지 않는다. 게시판(`app/api/board/`, `app/lesson/crawling/board/`)은 `NEXT_PUBLIC_API_URL` 백엔드로 fetch 프록시한다 (fastapi 쪽 `/api/board` 엔드포인트는 아직 미구현).

---

## 디렉터리 구조

```
taylor/
├── app/                    # Next.js App Router
│   ├── api/                # Route Handlers
│   │   ├── gemini/chat/    # Gemini AI 채팅
│   │   ├── chat/           # 채팅
│   │   ├── board/          # 게시판 CRUD
│   │   └── upload/         # 파일 업로드 (Vercel Blob)
│   ├── lesson/             # 교육 레슨
│   │   ├── titanic/        # 타이타닉 ML 수업
│   │   ├── crawling/       # 크롤링 실습 (게시판, 네이버 뉴스)
│   │   ├── agent/          # AI 에이전트 수업
│   │   ├── rag-system/     # RAG 시스템 수업
│   │   └── ...             # 기타 수업 (backend, devops, nlp, mobile, architecture)
│   ├── titanic/            # 타이타닉 데이터 뷰어
│   ├── login/              # 로그인
│   └── notice/             # 공지사항
└── components/
    ├── ui/                 # shadcn/ui 자동 생성 (직접 수정 금지)
    ├── home/               # 홈 페이지 컴포넌트
    ├── lesson/             # 레슨 공통 컴포넌트
    ├── titanic/            # 타이타닉 관련 컴포넌트
    ├── auth/               # 인증 컴포넌트
    └── layout/             # 레이아웃 컴포넌트
```

---

## 페이지 구조

| 경로 | 역할 |
|------|------|
| `/` | 홈 (Hero, Portfolio, Education, Contact) |
| `/lesson` | 교육 레슨 목록 |
| `/lesson/titanic` | 타이타닉 ML 수업 개요 |
| `/lesson/titanic/data-collection` | CSV 업로드·데이터 수집 실습 |
| `/lesson/titanic/passenger` | 승객 조회 실습 |
| `/lesson/titanic/captain` | 캡틴(관리자) 실습 |
| `/lesson/crawling/board` | 크롤링 실습 — 게시판 |
| `/lesson/crawling/naver-news` | 크롤링 실습 — 네이버 뉴스 |
| `/titanic` | 타이타닉 데이터 뷰어 |
| `/login` | 로그인 |
| `/notice` | 공지사항 |

---

## 컴포넌트 컨벤션

- 페이지별 컴포넌트는 `components/<페이지명>/` 하위에 둔다.
- `components/ui/`는 shadcn/ui 자동 생성 파일이므로 직접 수정하지 않는다.
- `next.config.mjs`의 `typescript.ignoreBuildErrors: true`는 의도된 설정이다 (빌드 시 타입 에러 무시).

## 다크 모드

구현 지시어: [_docs/darkmode-spec.md](_docs/darkmode-spec.md)
