from __future__ import annotations

import base64
import hashlib
import hmac
import time

_STATE_TTL = 600  # 10분 — authorize→callback 왕복 허용 시간


class OAuthStateGuard:
    """authorize→callback 왕복 동안 CSRF state와 PKCE code_verifier를 서버 저장 없이 운반한다."""

    def __init__(self, secret: str) -> None:
        self._secret = secret.encode()

    def issue(self, code_verifier: str = "") -> str:
        ts = str(int(time.time()))
        payload = f"{ts}:{code_verifier}"
        encoded = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
        sig = hmac.new(self._secret, encoded.encode(), hashlib.sha256).hexdigest()
        return f"{encoded}.{sig}"

    def verify(self, state: str) -> str | None:
        """유효하면 code_verifier(없으면 "")를 반환하고, 위·변조·만료 시 None을 반환한다."""
        encoded, _, sig = state.partition(".")
        if not sig:
            return None
        expected = hmac.new(self._secret, encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return None
        try:
            padded = encoded + "=" * (-len(encoded) % 4)
            payload = base64.urlsafe_b64decode(padded.encode()).decode()
        except ValueError:
            return None
        ts, _, code_verifier = payload.partition(":")
        if not ts.isdigit() or time.time() - int(ts) > _STATE_TTL:
            return None
        return code_verifier
