현재 상황 정리

[Windows 호스트]
  n8n (localhost:5678)          ← 지금 여기

[Docker]
  FastAPI (포트 8000 노출)
  Next.js (포트 3000 노출)
  pgvector (포트 5432)

n8n이 Docker 밖에 있으므로 FastAPI 호출 시 URL이 달라집니다.

- host.docker.internal:8000 → ❌ (Docker 내부에서 쓰는 주소)
- localhost:8000 → ✅ (호스트에서 호스트로)

---
다음 단계 (정책 §3 — 폴링 방식)

1. 화면 우측 하단 "Add first step..." 클릭
2. Gmail 검색 → 목록 하단 Triggers 섹션 → On message received 선택
3. 설정:
  - Poll Times = Every Minute
  - Event = Message Received
  - Simplify = ON
4. Gmail Credential 연결 (OAuth)
5. 그 뒤에 HTTP Request 노드 추가:
  - Method: POST
  - URL: http://localhost:8000/sherlock-homes/mary/receive
  - Body: JSON 필드 5개 (subject, from, to, preview, messageId)
