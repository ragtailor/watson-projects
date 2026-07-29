---
name: nextjs-missing-eslint-config
description: nextjs에 ESLint 설정 파일이 없어 pnpm lint가 동작하지 않는다 — 검증은 pnpm build로 한다
metadata: 
  node_type: memory
  type: project
  originSessionId: aa238371-5b90-4ede-8ffa-54850f278ec0
  modified: 2026-07-29T02:41:41.196Z
---

`nextjs/package.json`에 `"lint": "eslint ."`가 선언돼 있지만, 2026-07-29 확인 시점에
`eslint.config.*`도 `.eslintrc*`도 `package.json`의 `eslintConfig` 키도 없다.
설정 없이 실행되므로 `pnpm lint`는 실패할 가능성이 높다. 미해결 상태다.

**Why:** 프론트엔드 변경을 "린트 통과"로 검증하려 하면 도구 자체가 없어서 막힌다.
이 저장소의 nextjs에는 테스트 하네스도 없다.

**How to apply:** nextjs 변경의 검증 수단은 `pnpm build`다. `pnpm lint`를 성공 기준으로
삼지 않는다. 린트가 필요하다는 요청이 오면 먼저 ESLint 설정을 도입해야 한다고 알린다.

관련: [[subdoc-codename-vs-directory-path]]
