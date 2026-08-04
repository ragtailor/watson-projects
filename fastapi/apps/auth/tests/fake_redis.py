"""테스트용 인메모리 Redis 대역. 실제 Redis 없이 세션 저장소를 검증한다."""

from __future__ import annotations


class FakeRedis:
    def __init__(self) -> None:
        self._kv: dict[str, str] = {}
        self._sets: dict[str, set[str]] = {}
        self._hashes: dict[str, dict[str, str]] = {}
        self._ttl: dict[str, int] = {}

    # 문자열
    async def set(self, key, value, ex=None):
        self._kv[key] = value
        if ex is not None:
            self._ttl[key] = ex

    async def get(self, key):
        return self._kv.get(key)

    async def delete(self, *keys):
        for key in keys:
            self._kv.pop(key, None)
            self._sets.pop(key, None)
            self._hashes.pop(key, None)
            self._ttl.pop(key, None)

    # 해시
    async def hset(self, key, field, value):
        self._hashes.setdefault(key, {})[field] = value

    async def hget(self, key, field):
        return self._hashes.get(key, {}).get(field)

    async def hdel(self, key, *fields):
        bucket = self._hashes.get(key)
        if bucket is None:
            return 0
        removed = 0
        for field in fields:
            removed += 1 if bucket.pop(field, None) is not None else 0
        return removed

    async def hgetall(self, key):
        return dict(self._hashes.get(key, {}))

    # 집합
    async def sadd(self, key, *values):
        self._sets.setdefault(key, set()).update(values)

    async def srem(self, key, *values):
        self._sets.get(key, set()).difference_update(values)

    async def smembers(self, key):
        return set(self._sets.get(key, set()))

    # TTL
    async def expire(self, key, ttl):
        self._ttl[key] = ttl
        return True

    async def ttl(self, key):
        # 실제 Redis는 만료 없는 키에 -1, 없는 키에 -2를 준다.
        if key in self._ttl:
            return self._ttl[key]
        exists = key in self._kv or key in self._sets or key in self._hashes
        return -1 if exists else -2
