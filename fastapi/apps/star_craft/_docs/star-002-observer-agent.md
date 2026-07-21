# Harness: ConvNeXt Nano 이미지 분류 툴 구현

## 목적
ConvNeXt Nano 기반 이미지 분류 서비스를 RAG Tailor 인프라(dreamscape 네트워크, inception 레포)에 통합하고, MCP 도구로 노출하여 Claude Code / EXAONE 에이전트가 호출 가능하도록 한다.

## 실행 원칙 (Claude Code 준수 사항)
- 기존 아키텍처 컨벤션을 따를 것: clean architecture (hexagonal/port-adapter), 영화 테마 네이밍, FastAPI 백엔드 패턴
- 임의로 새 리포를 만들지 말 것. `inception` 레포 내부에 신규 서비스로 추가한다.
- 각 단계 완료 후 diff/결과를 요약하고 다음 단계로 넘어가기 전 확인받을 것 (승인 없이 임의로 스킵하지 말 것)
- 불필요한 주석, 임의 리팩터링, 요청 범위 밖 수정 금지
- 모든 설정값(포트, 경로, 모델명)은 `.env` 또는 config 파일로 분리, 하드코딩 금지

---

## Phase 1 — 모델 서빙 레이어

### 1.1 서비스 스캐폴딩
- 위치: `inception/services/image-classifier/`
- 구조 (clean architecture 적용):
  ```
  image-classifier/
    domain/          # 분류 결과 엔티티, 인터페이스
    application/      # 유스케이스 (ClassifyImageUseCase)
    infrastructure/   # ONNX Runtime 어댑터, timm 모델 로더
    api/               # FastAPI 라우터
    config.py
    main.py
  ```

### 1.2 모델 준비
- `timm`으로 `convnext_nano` pretrained 가중치 로드
- ONNX로 변환 후 저장 (`torch.onnx.export`), CPU 환경(N100) 기준 int8 quantization 적용 (`onnxruntime.quantization`)
- GPU 환경(Legion 4070) 배포 시엔 ONNX 우회, `torch.compile(mode="reduce-overhead")` 경로를 config 플래그로 분기 (`INFERENCE_BACKEND=onnx|torch`)

### 1.3 FastAPI 엔드포인트
- 포트: 8090 (기존 8000/8081/8082 다음 순번, `.env`에 `IMAGE_CLASSIFIER_PORT` 정의)
- 엔드포인트:
  ```
  POST /v1/classify
    request: multipart image file
    response: { "label": str, "confidence": float, "top5": [{label, confidence}] }
  GET /v1/health
  ```
- 입력 검증: 이미지 포맷/사이즈 제한, 실패 시 명확한 4xx 에러 바디 반환

### 1.4 인프라 연동
- `docker-compose`의 `dreamscape` 네트워크에 조인
- 동일 이미지 재요청 캐싱: 이미지 해시(sha256) 키로 `totem`(Redis)에 결과 캐싱, TTL 설정 가능하게

### 1.5 완료 기준
- `docker compose up image-classifier` 로 기동
- curl로 샘플 이미지 분류 테스트 통과
- `/v1/health` 200 응답

---

## Phase 2 — Tool 인터페이스 정의

### 2.1 Tool 스키마 작성
- 위치: `inception/services/image-classifier/tool_schema.json`
```json
{
  "name": "classify_image",
  "description": "이미지를 업로드하면 ConvNeXt Nano로 분류하여 라벨과 신뢰도를 반환",
  "input_schema": {
    "type": "object",
    "properties": {
      "image_path": { "type": "string", "description": "분류할 이미지 파일 경로 또는 URL" },
      "top_k": { "type": "integer", "default": 5 }
    },
    "required": ["image_path"]
  }
}
```

### 2.2 LLM 래퍼 작성 (EXAONE 에이전트용, 선택)
- 위치: `core/ai/vision_convnext.py` (기존 `lucy_anthropic.py`, `jarvis_gemini.py`와 동일 패턴)
- 역할: tool_schema 기반 요청 파싱 → `/v1/classify` 호출 → 결과를 에이전트 응답 포맷으로 정규화
- `core/lol/` 오케스트레이션 레이어에 tool 등록 (`worlds_`/`rift_` 접두사 컨벤션 확인 후 적용)

---

## Phase 3 — MCP 서버로 노출 (Claude Code / Desktop용)

### 3.1 MCP 서버 스캐폴딩
- 위치: `inception/services/image-classifier/mcp_server/`
- Python `mcp` SDK 사용
- `list_tools()` → `classify_image` 등록 (Phase 2.1 스키마 재사용)
- `call_tool()` → 내부적으로 `/v1/classify` HTTP 호출 후 결과 반환

### 3.2 로컬 연결 설정
- Claude Code MCP 설정 파일에 서버 등록 (stdio 또는 SSE transport 선택, 기존 다른 MCP 서버 있으면 방식 통일)
- 연결 테스트: Claude Code에서 "이 이미지 분류해줘" 요청 시 도구 자동 호출 확인

### 3.3 완료 기준
- Claude Code가 로컬 MCP 서버를 인식하고 `classify_image` 도구 목록에 노출
- 실제 이미지 경로로 호출 시 정상 결과 반환

---

## 산출물 체크리스트
- [ ] `inception/services/image-classifier/` 전체 구조
- [ ] ONNX 변환 모델 파일 및 로더
- [ ] FastAPI `/v1/classify`, `/v1/health` 엔드포인트
- [ ] docker-compose 서비스 항목 (dreamscape 네트워크, totem 캐싱)
- [ ] `tool_schema.json`
- [ ] (선택) `core/ai/vision_convnext.py`
- [ ] MCP 서버 (`mcp_server/`)
- [ ] README: 배포/테스트 방법

## 진행 방식
Phase 1 → 승인 → Phase 2 → 승인 → Phase 3 순서로 진행. 각 Phase 완료 시 변경된 파일 목록과 테스트 결과를 요약 보고할 것.