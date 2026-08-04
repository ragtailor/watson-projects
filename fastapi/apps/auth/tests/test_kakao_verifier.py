"""카카오 OIDC id_token 검증 테스트.

카카오 서버를 부르지 않는다. 로컬 RSA 키로 id_token을 만들고, JWKS 조회만 가로챈다.
"""

from __future__ import annotations

import json
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

from auth.oidc import kakao_verifier as verifier
from auth.oidc.kakao_verifier import KakaoKeyUnavailable, KakaoVerifyError

_CLIENT_ID = "kakao-rest-api-key"
_JWKS_URI = "https://kauth.kakao.com/.well-known/jwks.json"


def _new_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _jwk_of(key: rsa.RSAPrivateKey, kid: str) -> dict:
    jwk = json.loads(RSAAlgorithm.to_jwk(key.public_key()))
    jwk.update({"kid": kid, "alg": "RS256", "use": "sig"})
    return jwk


def _id_token(
    key: rsa.RSAPrivateKey,
    kid: str,
    *,
    aud: str = _CLIENT_ID,
    nonce: str = "nonce-1",
    expires_in: int = 300,
    sub: str = "1234567890",
) -> str:
    now = int(time.time())
    payload = {
        "iss": "https://kauth.kakao.com",
        "aud": aud,
        "sub": sub,
        "iat": now,
        "auth_time": now,
        "exp": now + expires_in,
        "nonce": nonce,
        "nickname": "테스터",
        "email": "tester@example.com",
    }
    return jwt.encode(payload, key, algorithm="RS256", headers={"kid": kid})


class _Jwks:
    """JWKS 조회를 가로채고 호출 횟수를 센다."""

    def __init__(self, keys: list[dict]) -> None:
        self.keys = keys
        self.jwks_calls = 0
        self.fail = False

    async def fetch(self, client, url: str) -> dict:
        if self.fail:
            raise RuntimeError("네트워크 오류")
        if "openid-configuration" in url:
            return {"issuer": "https://kauth.kakao.com", "jwks_uri": _JWKS_URI}
        self.jwks_calls += 1
        return {"keys": self.keys}


@pytest.fixture
def kakao(monkeypatch):
    monkeypatch.setenv("KAKAO_CLIENT_ID", _CLIENT_ID)
    verifier.reset_cache()

    key = _new_key()
    jwks = _Jwks([_jwk_of(key, "kid-1")])
    monkeypatch.setattr(verifier, "_fetch_json", jwks.fetch)
    yield key, jwks
    verifier.reset_cache()


async def test_valid_id_token_returns_identity(kakao):
    key, _ = kakao
    identity = await verifier.verify_id_token(_id_token(key, "kid-1"), "nonce-1")
    assert identity.sub == "1234567890"
    assert identity.email == "tester@example.com"
    assert identity.nickname == "테스터"


async def test_forged_signature_is_rejected(kakao):
    _, _jwks = kakao
    attacker = _new_key()  # 카카오 키가 아닌 키로 서명
    with pytest.raises(KakaoVerifyError):
        await verifier.verify_id_token(_id_token(attacker, "kid-1"), "nonce-1")


async def test_wrong_audience_is_rejected(kakao):
    key, _ = kakao
    token = _id_token(key, "kid-1", aud="other-app-key")
    with pytest.raises(KakaoVerifyError):
        await verifier.verify_id_token(token, "nonce-1")


async def test_expired_token_is_rejected(kakao):
    key, _ = kakao
    token = _id_token(key, "kid-1", expires_in=-10)
    with pytest.raises(KakaoVerifyError):
        await verifier.verify_id_token(token, "nonce-1")


async def test_nonce_mismatch_is_rejected(kakao):
    key, _ = kakao
    token = _id_token(key, "kid-1", nonce="nonce-from-attacker")
    with pytest.raises(KakaoVerifyError):
        await verifier.verify_id_token(token, "nonce-1")


async def test_jwks_is_cached_and_refreshed_only_on_kid_miss(kakao):
    key, jwks = kakao

    await verifier.verify_id_token(_id_token(key, "kid-1"), "nonce-1")
    await verifier.verify_id_token(_id_token(key, "kid-1"), "nonce-1")
    assert jwks.jwks_calls == 1  # 두 번째 요청은 캐시로 처리

    # 키 롤오버: 새 kid로 서명된 토큰이 오면 그때만 다시 조회한다.
    rolled = _new_key()
    jwks.keys = [_jwk_of(rolled, "kid-2")]
    identity = await verifier.verify_id_token(_id_token(rolled, "kid-2"), "nonce-1")
    assert identity.sub == "1234567890"
    assert jwks.jwks_calls == 2


async def test_unknown_kid_after_refresh_is_token_error(kakao):
    key, jwks = kakao
    stranger = _new_key()
    with pytest.raises(KakaoVerifyError):
        await verifier.verify_id_token(_id_token(stranger, "kid-unknown"), "nonce-1")
    assert jwks.jwks_calls == 1  # 갱신은 한 번만 시도한다


async def test_jwks_unavailable_without_cache_is_503(kakao):
    key, jwks = kakao
    jwks.fail = True
    with pytest.raises(KakaoKeyUnavailable):
        await verifier.verify_id_token(_id_token(key, "kid-1"), "nonce-1")


async def test_cached_key_survives_jwks_outage(kakao):
    key, jwks = kakao
    await verifier.verify_id_token(_id_token(key, "kid-1"), "nonce-1")

    jwks.fail = True
    verifier._expires_at = 0.0  # 캐시 만료 상태로 만들어 갱신을 시도하게 한다
    identity = await verifier.verify_id_token(_id_token(key, "kid-1"), "nonce-1")
    assert identity.sub == "1234567890"


async def test_missing_client_id_is_503(kakao, monkeypatch):
    key, _ = kakao
    monkeypatch.delenv("KAKAO_CLIENT_ID", raising=False)
    with pytest.raises(KakaoKeyUnavailable):
        await verifier.verify_id_token(_id_token(key, "kid-1"), "nonce-1")
