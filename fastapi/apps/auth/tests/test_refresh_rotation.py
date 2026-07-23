"""리프레시 로테이션/재사용 테스트. (완료 기준 3의 리프레시 재사용 항목)

Redis는 인메모리 FakeRedis로 대체한다(실제 Redis 불필요).
"""

from __future__ import annotations

import pytest

from auth import services
from auth.rbac import Provider


class FakeRedis:
    def __init__(self) -> None:
        self._kv: dict[str, str] = {}
        self._sets: dict[str, set[str]] = {}

    async def set(self, key, value, ex=None):
        self._kv[key] = value

    async def get(self, key):
        return self._kv.get(key)

    async def delete(self, *keys):
        for key in keys:
            self._kv.pop(key, None)
            self._sets.pop(key, None)

    async def sadd(self, key, *values):
        self._sets.setdefault(key, set()).update(values)

    async def srem(self, key, *values):
        self._sets.get(key, set()).difference_update(values)

    async def smembers(self, key):
        return set(self._sets.get(key, set()))

    async def expire(self, key, ttl):
        return True


@pytest.fixture
def fake_redis(monkeypatch):
    client = FakeRedis()
    monkeypatch.setattr(services, "_redis", lambda: client)
    return client


async def test_rotation_issues_new_refresh(fake_redis):
    tokens = await services.login(Provider.GOOGLE, "code-abc")
    rotated = await services.refresh(tokens.refresh_token)
    assert rotated.refresh_token != tokens.refresh_token
    assert rotated.access_token


async def test_reuse_of_rotated_token_revokes_whole_session(fake_redis):
    tokens = await services.login(Provider.GOOGLE, "code-abc")
    original_refresh = tokens.refresh_token

    rotated = await services.refresh(original_refresh)  # 정상 로테이션

    # 이미 로테이션된 원본을 재사용 → 재사용 감지 + 세션 전체 폐기
    with pytest.raises(services.RefreshReuseError):
        await services.refresh(original_refresh)

    # 세션이 폐기됐으므로 방금 발급된 rotated 리프레시도 더는 통하지 않는다
    with pytest.raises(services.RefreshError):
        await services.refresh(rotated.refresh_token)


async def test_unknown_but_valid_signature_is_reuse(fake_redis):
    # 저장소에 없는(로그인 없이 만든) 유효 서명 토큰 → 재사용으로 간주
    orphan = services.create_refresh_token("google:ghost")
    with pytest.raises(services.RefreshReuseError):
        await services.refresh(orphan)
