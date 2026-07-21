"""로그인 게이트 (003) — 앱 바깥층에 얹는 인증 미들웨어.

기존 라우터/비즈니스 로직은 수정하지 않는다. .env 의 AUTH_ID / AUTH_PW /
SESSION_SECRET 를 읽어 단일 계정 세션 쿠키 로그인을 제공한다.

- 미인증 GET → /login 리다이렉트 (로그인 페이지, GitLab 모티브)
- /health 만 인증 없이 허용, /logout 으로 세션 해제
- 비밀번호 비교는 secrets.compare_digest (타이밍 공격 완화)
- 반복 실패 시 지연 (최소한의 브루트포스 완화)
"""

import asyncio
import hashlib
import hmac
import html
import os
import secrets
import time
from urllib.parse import parse_qs, quote

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

COOKIE_NAME = "gate_session"
SESSION_TTL = 12 * 60 * 60  # 12시간
FAIL_WINDOW = 15 * 60  # 실패 카운트 집계 구간(초)
FAIL_FREE_TRIES = 2  # 이 횟수까지는 지연 없음
FAIL_MAX_DELAY = 5  # 최대 지연(초)

_LOGIN_PAGE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__SERVICE__ · Sign in</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
      "Noto Sans KR", sans-serif;
    background: #ffffff; color: #28272d;
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
  }
  .card {
    width: 100%; max-width: 380px; margin: 16px;
    border: 1px solid #dcdcde; border-top: 3px solid #FC6D26;
    border-radius: 8px; padding: 40px 32px 32px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, .06);
  }
  .mark {
    width: 40px; height: 40px; margin: 0 auto 16px; border-radius: 10px;
    background: linear-gradient(135deg, #FC6D26, #E24329);
  }
  h1 { font-size: 18px; text-align: center; color: #171321; margin-bottom: 4px; }
  p.sub { font-size: 13px; text-align: center; color: #737278; margin-bottom: 24px; }
  label {
    display: block; font-size: 13px; font-weight: 600;
    margin: 14px 0 6px; color: #28272d;
  }
  input {
    width: 100%; padding: 10px 12px; font-size: 14px;
    border: 1px solid #bfbfc3; border-radius: 4px; background: #fff;
  }
  input:focus { outline: 2px solid #6E49CB; outline-offset: -1px; border-color: #6E49CB; }
  button {
    width: 100%; margin-top: 22px; padding: 11px 0; font-size: 14px; font-weight: 600;
    color: #fff; background: #FC6D26; border: 0; border-radius: 4px; cursor: pointer;
  }
  button:hover { background: #E24329; }
  .error {
    margin-bottom: 4px; padding: 10px 12px; font-size: 13px;
    color: #dd2b0e; background: #fdf1ef; border: 1px solid #f5c8c2; border-radius: 4px;
  }
</style>
</head>
<body>
  <form class="card" method="post" action="/login">
    <div class="mark"></div>
    <h1>__SERVICE__</h1>
    <p class="sub">계속하려면 로그인하세요</p>
    __ERROR__
    <label for="username">Username</label>
    <input id="username" name="username" type="text" autocomplete="username" autofocus required>
    <label for="password">Password</label>
    <input id="password" name="password" type="password" autocomplete="current-password" required>
    <input type="hidden" name="next" value="__NEXT__">
    <button type="submit">로그인</button>
  </form>
</body>
</html>
"""

_ERROR_HTML = '<div class="error">아이디 또는 비밀번호가 올바르지 않습니다.</div>'

# IP별 최근 로그인 실패 시각 (프로세스 메모리, 최소한의 완화 장치)
_failures: dict[str, list[float]] = {}


def _make_token(secret: bytes) -> str:
    ts = str(int(time.time()))
    sig = hmac.new(secret, ts.encode(), hashlib.sha256).hexdigest()
    return f"{ts}.{sig}"


def _verify_token(secret: bytes, token: str) -> bool:
    ts, _, sig = token.partition(".")
    if not ts.isdigit() or not sig:
        return False
    if time.time() - int(ts) > SESSION_TTL:
        return False
    expected = hmac.new(secret, ts.encode(), hashlib.sha256).hexdigest()
    return secrets.compare_digest(expected, sig)


def _safe_next(raw: str) -> str:
    """오픈 리다이렉트 방지: 사이트 내부 경로만 허용."""
    if raw.startswith("/") and not raw.startswith("//"):
        return raw
    return "/"


def _fail_delay(ip: str) -> int:
    now = time.time()
    recent = [t for t in _failures.get(ip, []) if now - t < FAIL_WINDOW]
    _failures[ip] = recent
    if len(recent) <= FAIL_FREE_TRIES:
        return 0
    return min(len(recent) - FAIL_FREE_TRIES, FAIL_MAX_DELAY)


def _render_login(service_name: str, next_path: str, error: bool) -> HTMLResponse:
    page = (
        _LOGIN_PAGE
        .replace("__SERVICE__", html.escape(service_name))
        .replace("__NEXT__", html.escape(next_path, quote=True))
        .replace("__ERROR__", _ERROR_HTML if error else "")
    )
    return HTMLResponse(page, status_code=401 if error else 200)


def install_login_gate(app, service_name: str) -> None:
    """FastAPI 앱에 로그인 게이트 미들웨어를 설치한다."""
    auth_id = os.getenv("AUTH_ID", "")
    auth_pw = os.getenv("AUTH_PW", "")
    session_secret = os.getenv("SESSION_SECRET", "")
    missing = [
        k for k, v in {
            "AUTH_ID": auth_id, "AUTH_PW": auth_pw, "SESSION_SECRET": session_secret,
        }.items() if not v or v == "CHANGE_ME"
    ]
    if missing:
        raise RuntimeError(f"login_gate: .env 값이 설정되지 않았습니다: {', '.join(missing)}")
    secret = session_secret.encode()

    async def _handle_login_post(request: Request) -> Response:
        try:
            form = parse_qs((await request.body()).decode())
        except UnicodeDecodeError:
            form = {}
        username = form.get("username", [""])[0]
        password = form.get("password", [""])[0]
        next_path = _safe_next(form.get("next", ["/"])[0])
        ip = request.client.host if request.client else "unknown"

        delay = _fail_delay(ip)
        if delay:
            await asyncio.sleep(delay)

        id_ok = secrets.compare_digest(username.encode(), auth_id.encode())
        pw_ok = secrets.compare_digest(password.encode(), auth_pw.encode())
        if id_ok & pw_ok:
            _failures.pop(ip, None)
            resp = RedirectResponse(next_path, status_code=302)
            resp.set_cookie(
                COOKIE_NAME, _make_token(secret),
                max_age=SESSION_TTL, path="/",
                httponly=True, secure=True, samesite="lax",
            )
            return resp
        _failures.setdefault(ip, []).append(time.time())
        return _render_login(service_name, next_path, error=True)

    async def dispatch(request: Request, call_next):
        path = request.url.path
        if request.method == "OPTIONS":  # CORS preflight는 통과
            return await call_next(request)
        if path == "/health":
            return JSONResponse({"status": "ok"})
        # 소셜 로그인(OAuth) 인가·콜백 경로 — 사이트 게이트를 몰라도 실제 로그인이 가능해야 한다.
        if path.startswith("/api/kingsman/oauth/"):
            return await call_next(request)
        if path == "/login":
            if request.method == "GET":
                next_path = _safe_next(request.query_params.get("next", "/"))
                return _render_login(service_name, next_path, error=False)
            if request.method == "POST":
                return await _handle_login_post(request)
            return Response(status_code=405)
        if path == "/logout":
            resp = RedirectResponse("/login", status_code=302)
            resp.delete_cookie(COOKIE_NAME, path="/")
            return resp

        token = request.cookies.get(COOKIE_NAME, "")
        if _verify_token(secret, token):
            return await call_next(request)
        if request.method == "GET":
            target = path + (f"?{request.url.query}" if request.url.query else "")
            return RedirectResponse(f"/login?next={quote(target, safe='')}", status_code=302)
        return JSONResponse({"detail": "authentication required"}, status_code=401)

    app.add_middleware(BaseHTTPMiddleware, dispatch=dispatch)
