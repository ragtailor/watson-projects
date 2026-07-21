import time

from kingsman.adapter.outbound.session.oauth_state_guard import OAuthStateGuard


def test_issue_then_verify_roundtrips_code_verifier():
    guard = OAuthStateGuard(secret="test-secret")

    state = guard.issue("pkce-verifier-value")

    assert guard.verify(state) == "pkce-verifier-value"


def test_verify_returns_empty_string_when_no_code_verifier():
    guard = OAuthStateGuard(secret="test-secret")

    state = guard.issue()

    assert guard.verify(state) == ""


def test_verify_rejects_tampered_state():
    guard = OAuthStateGuard(secret="test-secret")
    state = guard.issue("verifier")
    encoded, _, _sig = state.partition(".")

    tampered = f"{encoded}.deadbeef"

    assert guard.verify(tampered) is None


def test_verify_rejects_state_signed_with_different_secret():
    issuer = OAuthStateGuard(secret="secret-a")
    verifier = OAuthStateGuard(secret="secret-b")

    state = issuer.issue("verifier")

    assert verifier.verify(state) is None


def test_verify_rejects_expired_state():
    guard = OAuthStateGuard(secret="test-secret")
    state = guard.issue("verifier")

    # TTL(10분)을 초과한 것처럼 보이도록 payload의 timestamp를 과거로 바꿔 재서명한다.
    import base64
    import hashlib
    import hmac

    encoded, _, _sig = state.partition(".")
    padded = encoded + "=" * (-len(encoded) % 4)
    payload = base64.urlsafe_b64decode(padded.encode()).decode()
    _, _, code_verifier = payload.partition(":")
    old_ts = str(int(time.time()) - 700)
    old_payload = f"{old_ts}:{code_verifier}"
    old_encoded = base64.urlsafe_b64encode(old_payload.encode()).decode().rstrip("=")
    old_sig = hmac.new(b"test-secret", old_encoded.encode(), hashlib.sha256).hexdigest()
    expired_state = f"{old_encoded}.{old_sig}"

    assert guard.verify(expired_state) is None
