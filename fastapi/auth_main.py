"""인증 게이트웨이 엔트리포인트 — auth.ragtailor.com 전용.

비즈니스 백엔드(main.py)와 별도 컨테이너로 기동한다. 토큰 발급은 이 컨테이너에서만
이뤄지며, 개인키(JWT_PRIVATE_KEY)는 여기에만 존재한다.

    uvicorn auth_main:app --host 0.0.0.0 --port 9000
"""

import os
import sys

_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _root)                      # core.* 임포트
sys.path.insert(0, os.path.join(_root, "apps"))  # auth.* 임포트 (repo 컨벤션: bare 앱 이름)

from fastapi import FastAPI

from auth.router import router as auth_router

app = FastAPI(
    title="RAG Tailor Auth",
    docs_url=None, redoc_url=None, openapi_url=None,  # 실서비스: 문서 비노출
)
app.include_router(auth_router, prefix="/auth")


@app.get("/healthz")
async def healthz():
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("auth_main:app", host="0.0.0.0", port=9000)
