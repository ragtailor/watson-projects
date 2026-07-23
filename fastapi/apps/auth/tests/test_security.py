"""검증부 테스트 — auth 발급 토큰을 공개키만으로 검증. (완료 기준 3의 토큰 항목)"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

import pytest

from core import config
from core.security import TokenError, create_access_token, verify_token

AUD = "ragtaylor-api"


def _b64url(data: dict) -> str:
    raw = json.dumps(data).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def test_roundtrip_verified_with_public_key_only():
    token = create_access_token(sub="u1", roles=["user"], aud=AUD)
    payload = verify_token(token, aud=AUD)
    assert payload.sub == "u1"
    assert payload.roles == ["user"]
    assert payload.aud == AUD
    assert payload.jti


def test_wrong_audience_is_rejected():
    token = create_access_token(sub="u1", roles=["user"], aud=AUD)
    with pytest.raises(TokenError):
        verify_token(token, aud="acoder-api")


def test_expired_token_is_rejected():
    token = create_access_token(sub="u1", roles=["user"], aud=AUD, expires_min=-1)
    with pytest.raises(TokenError):
        verify_token(token, aud=AUD)


def test_tampered_signature_is_rejected():
    token = create_access_token(sub="u1", roles=["user"], aud=AUD)
    head, body, sig = token.split(".")
    flipped = sig[:-1] + ("A" if sig[-1] != "A" else "B")
    with pytest.raises(TokenError):
        verify_token(f"{head}.{body}.{flipped}", aud=AUD)


def test_alg_none_token_is_rejected():
    now = int(time.time())
    header = _b64url({"alg": "none", "typ": "JWT"})
    body = _b64url({
        "sub": "u1", "roles": ["admin"], "aud": AUD,
        "iat": now, "exp": now + 600, "jti": "forged",
    })
    forged = f"{header}.{body}."
    with pytest.raises(TokenError):
        verify_token(forged, aud=AUD)


def test_hs256_forced_token_is_rejected():
    # 공개키를 HMAC 비밀키로 악용한 알고리즘 혼동 공격.
    # (토큰을 수동 서명해 verify_token 까지 도달시킨다 — RS256 리터럴이 거부해야 한다.)
    now = int(time.time())
    public_pem = config.get_jwt_public_key()
    header = _b64url({"alg": "HS256", "typ": "JWT"})
    body = _b64url({
        "sub": "u1", "roles": ["admin"], "aud": AUD,
        "iat": now, "exp": now + 600, "jti": "forged",
    })
    signing_input = f"{header}.{body}".encode("ascii")
    signature = base64.urlsafe_b64encode(
        hmac.new(public_pem.encode("utf-8"), signing_input, hashlib.sha256).digest()
    ).rstrip(b"=").decode("ascii")
    forged = f"{header}.{body}.{signature}"
    with pytest.raises(TokenError):
        verify_token(forged, aud=AUD)
