---
name: docs-update-verify-against-repo
description: 사용자가 붙여넣은 템플릿으로 문서를 갱신할 때는 항목 목차로만 쓰고 값은 저장소에서 검증해 채운다
metadata: 
  node_type: memory
  type: feedback
  originSessionId: aa238371-5b90-4ede-8ffa-54850f278ec0
  modified: 2026-07-29T02:41:25.316Z
---

문서(특히 CLAUDE.md) 갱신을 요청하며 다른 프로젝트의 템플릿을 붙여넣는 경우가 있다.
2026-07-29에는 Node.js/Express 단일 서버용 템플릿(`npm run dev`, Jest + Supertest,
`src/errors/`, `src/legacy/`, payments PCI 체크리스트)을 주며 "누락된 사항이 있으면
추가해주고, 기존 내용은 수정하지 마"라고 요청했다. 이 저장소는 fastapi + nextjs +
flutter 모노레포라 스택이 전혀 달랐다.

**Why:** 템플릿을 그대로 붙이면 존재하지 않는 명령어·디렉터리·모듈을 지시하는
거짓 문서가 된다. 사용자가 원한 것은 템플릿의 *내용*이 아니라 "이런 항목들이
빠져 있다"는 *목차*였다.

**How to apply:**
- 붙여넣은 내용은 **섹션 목록으로만** 취급한다. 각 항목의 값은 저장소를 직접 읽어
  채운다 (package.json, pytest.ini, docker-compose.yml, .env.example, git log 등).
- 템플릿에 있으나 저장소에 실물이 없는 항목(`src/legacy/`, payments 모듈 등)은
  **넣지 않는다.** 대신 실재하는 동종 항목으로 대체한다.
- 확인 불가능한 항목(예: 브랜치 전략)은 추측하지 말고 AskUserQuestion으로 묻는다.
  실제 git 상태를 근거로 선택지를 제시하면 판단이 빨랐다.
- "기존 내용은 수정하지 마"는 문자 그대로 지킨다. 작업 후
  `git diff --stat`으로 `insertions`만 있고 `deletions`가 0인지 검증해 보고한다.

관련: [[subdoc-codename-vs-directory-path]]
