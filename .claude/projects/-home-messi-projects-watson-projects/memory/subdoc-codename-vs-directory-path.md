---
name: subdoc-codename-vs-directory-path
description: 하위 CLAUDE.md의 tailor/taylor는 서비스 코드네임이며 디렉터리 경로가 아니다 — 경로만 실제 이름으로 정리했다
metadata: 
  node_type: memory
  type: project
  originSessionId: aa238371-5b90-4ede-8ffa-54850f278ec0
  modified: 2026-07-29T02:41:34.932Z
---

하위 CLAUDE.md들이 실제 디렉터리명 대신 코드네임을 경로로 써서 동작하지 않는
명령어를 안내하고 있었다. 2026-07-29에 **경로만** 실제 디렉터리명으로 정리했다.

- `fastapi/CLAUDE.md`, `fastapi/apps/titanic/_docs/CLAUDE.md`,
  `fastapi/apps/dumb_and_dumber/_docs/CLAUDE.md`: `cd tailor` → `cd fastapi`
- `nextjs/CLAUDE.md`: `cd taylor` → `cd nextjs`

**의도적으로 남긴 것 — 코드네임이지 경로가 아니다:**

- `fastapi/CLAUDE.md:1` `# Backend — tailor`
- `nextjs/CLAUDE.md:1` `# Frontend — taylor`
- `nextjs/CLAUDE.md:26` 주석 `# tailor 백엔드`
- `api.ragtaylor.com`(실배포 도메인), `com.ragtailor`(저장소 이름)은 실물이므로 불가침

**Why:** 표기가 `tailor` / `taylor` / `ragtailor` / `ragtaylor` 네 갈래로 갈려 있어
일괄 치환하면 도메인이나 저장소 이름까지 망가진다. 코드네임 통일 여부는 사용자가
아직 결정하지 않았다.

**How to apply:** 이 저장소에서 `tailor`/`taylor`를 만나면 **경로인지 이름인지 먼저
구분한다.** 경로면 `fastapi`/`nextjs`로 고치고, 제목·주석·도메인이면 손대지 않는다.
일괄 `sed` 치환은 쓰지 않는다.

관련: [[docs-update-verify-against-repo]]
