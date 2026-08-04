"""리프레시 로테이션/재사용 테스트. (완료 기준 3의 리프레시 재사용 항목)

Redis는 인메모리 FakeRedis로 대체한다(실제 Redis 불필요).
플랫폼 분리는 test_platform_sessions.py에서 따로 검증한다.
"""

from __future__ import annotations

import pytest

from auth import services
from auth.rbac import Platform, Provider
from auth.store import refresh_store
from auth.tests.fake_redis import FakeRedis


@pytest.fixture
def fake_redis(monkeypatch):
    client = FakeRedis()
    monkeypatch.setattr(refresh_store, "_redis", lambda: client)
    return client


async def test_rotation_issues_new_refresh(fake_redis):
    tokens = await services.login(Provider.GOOGLE, "code-abc")
    rotated = await services.refresh(tokens.refresh_token, Platform.WEB)
    assert rotated.refresh_token != tokens.refresh_token
    assert rotated.access_token


async def test_reuse_of_rotated_token_revokes_that_session(fake_redis):
    tokens = await services.login(Provider.GOOGLE, "code-abc")
    original_refresh = tokens.refresh_token

    rotated = await services.refresh(original_refresh, Platform.WEB)  # 정상 로테이션

    # 이미 로테이션된 원본을 재사용 → 재사용 감지 + 해당 플랫폼 세션 폐기
    with pytest.raises(services.RefreshReuseError):
        await services.refresh(original_refresh, Platform.WEB)

    # 세션이 폐기됐으므로 방금 발급된 rotated 리프레시도 더는 통하지 않는다
    with pytest.raises(services.RefreshError):
        await services.refresh(rotated.refresh_token, Platform.WEB)


async def test_unknown_but_valid_signature_is_reuse(fake_redis):
    # 저장소에 없는(로그인 없이 만든) 유효 서명 토큰 → 재사용으로 간주
    orphan = services.create_refresh_token("google:ghost", platform=Platform.WEB.value)
    with pytest.raises(services.RefreshReuseError):
        await services.refresh(orphan, Platform.WEB)


async def test_token_without_platform_claim_is_rejected(fake_redis):
    # 플랫폼 분리 도입 이전에 발급된 토큰 → 갱신 거부(1회 재로그인 유도)
    legacy = services.create_refresh_token("google:legacy")
    with pytest.raises(services.PlatformMismatchError):
        await services.refresh(legacy, Platform.WEB)


async def test_refresh_token_is_not_stored_in_plaintext(fake_redis):
    tokens = await services.login(Provider.GOOGLE, "code-abc")

    stored = "".join(
        value
        for fields in fake_redis._hashes.values()
        for value in fields.values()
    )
    assert tokens.refresh_token not in stored
    assert refresh_store.token_hash(tokens.refresh_token) in stored
