from __future__ import annotations

import hashlib
import hmac
import time

from kingsman.app.ports.output.user_session_port import UserSessionPort

_SESSION_TTL = 12 * 60 * 60  # 12시간, login_gate.py의 SESSION_TTL과 동일한 정책


class SignedCookieSessionAdapter(UserSessionPort):
    """HMAC 서명 쿠키 기반 세션 — login_gate.py의 토큰 방식과 동일한 원리를 사용자 단위로 적용."""

    def __init__(self, secret: str) -> None:
        self._secret = secret.encode()

    def issue(self, user_id: str) -> str:
        ts = str(int(time.time()))
        payload = f"{ts}.{user_id}"
        sig = hmac.new(self._secret, payload.encode(), hashlib.sha256).hexdigest()
        return f"{payload}.{sig}"

    def verify(self, token: str) -> str | None:
        ts, _, rest = token.partition(".")
        user_id, _, sig = rest.rpartition(".")
        if not ts.isdigit() or not user_id or not sig:
            return None
        if time.time() - int(ts) > _SESSION_TTL:
            return None
        expected = hmac.new(self._secret, f"{ts}.{user_id}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return None
        return user_id
