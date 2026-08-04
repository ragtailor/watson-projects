"""모바일/웹 세션 분리 테스트 (FAST-003 회귀 시나리오).

카카오 검증과 DB 접근은 대역으로 갈아끼운다 — 이 테스트가 보는 것은 플랫폼 분리다.
"""

from __future__ import annotations

import pytest

from auth import services
from auth.oidc.kakao_verifier import KakaoIdentity
from auth.rbac import Platform
from auth.store import refresh_store
from auth.tests.fake_redis import FakeRedis

_SUB = "1234567890"
_USER_ID = f"kakao_{_SUB}"


@pytest.fixture
def env(monkeypatch):
    """카카오 검증·DB 없이 kakao_login이 돌게 만든다."""
    client = FakeRedis()
    monkeypatch.setattr(refresh_store, "_redis", lambda: client)

    async def fake_verify(id_token: str, nonce: str) -> KakaoIdentity:
        return KakaoIdentity(sub=_SUB, email="tester@example.com", nickname="테스터")

    async def fake_resolve(identity: KakaoIdentity) -> str:
        return _USER_ID

    monkeypatch.setattr(services, "verify_id_token", fake_verify)
    monkeypatch.setattr(services, "_resolve_user", fake_resolve)
    return client


async def _login(platform: Platform):
    return await services.kakao_login("id-token", platform, "nonce-1")


async def test_login_issues_platform_scoped_tokens(env):
    mobile = await _login(Platform.MOBILE)
    assert mobile.platform == Platform.MOBILE.value

    # 두 슬롯이 같은 해시 안에 독립적으로 존재한다.
    web = await _login(Platform.WEB)
    slots = await env.hgetall(f"auth:session:{_USER_ID}")
    assert set(slots) == {"mobile", "web"}
    assert mobile.access_token != web.access_token


async def test_mobile_token_cannot_refresh_web_session(env):
    mobile = await _login(Platform.MOBILE)
    with pytest.raises(services.PlatformMismatchError):
        await services.refresh(mobile.refresh_token, Platform.WEB)

    # 거부됐을 뿐 모바일 세션은 멀쩡하다.
    rotated = await services.refresh(mobile.refresh_token, Platform.MOBILE)
    assert rotated.platform == Platform.MOBILE.value


async def test_mobile_logout_keeps_web_session(env):
    mobile = await _login(Platform.MOBILE)
    web = await _login(Platform.WEB)

    await services.logout(mobile.refresh_token, Platform.MOBILE)

    slots = await env.hgetall(f"auth:session:{_USER_ID}")
    assert set(slots) == {"web"}

    # 웹 세션은 계속 갱신된다.
    rotated = await services.refresh(web.refresh_token, Platform.WEB)
    assert rotated.platform == Platform.WEB.value

    # 모바일은 끊겼다.
    with pytest.raises(services.RefreshError):
        await services.refresh(mobile.refresh_token, Platform.MOBILE)


async def test_mobile_reuse_does_not_kill_web_session(env):
    mobile = await _login(Platform.MOBILE)
    web = await _login(Platform.WEB)

    await services.refresh(mobile.refresh_token, Platform.MOBILE)  # 로테이션
    with pytest.raises(services.RefreshReuseError):
        await services.refresh(mobile.refresh_token, Platform.MOBILE)  # 재사용

    rotated = await services.refresh(web.refresh_token, Platform.WEB)
    assert rotated.platform == Platform.WEB.value


async def test_logout_with_other_platform_token_is_ignored(env):
    mobile = await _login(Platform.MOBILE)
    await _login(Platform.WEB)

    # 모바일 토큰으로 웹 로그아웃을 시도해도 웹 슬롯은 지워지지 않는다.
    await services.logout(mobile.refresh_token, Platform.WEB)

    slots = await env.hgetall(f"auth:session:{_USER_ID}")
    assert set(slots) == {"mobile", "web"}


async def test_platform_ttls_are_independent(env, monkeypatch):
    monkeypatch.setenv("ACCESS_TTL_MOBILE_MIN", "60")
    monkeypatch.setenv("ACCESS_TTL_WEB_MIN", "30")

    mobile = await _login(Platform.MOBILE)
    web = await _login(Platform.WEB)

    assert mobile.expires_in == 60 * 60
    assert web.expires_in == 30 * 60
