from __future__ import annotations

import os

from redis.asyncio import Redis

_client: Redis | None = None


def init_client() -> None:
    global _client
    if _client is not None:
        return

    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return

    _client = Redis.from_url(redis_url, decode_responses=True)


def get_client() -> Redis:
    if _client is None:
        init_client()

    if _client is None:
        raise RuntimeError("REDIS_URL이 설정되지 않아 Redis 클라이언트를 초기화할 수 없습니다.")

    return _client


async def dispose_client() -> None:
    global _client
    if _client is not None:
        await _client.close()
    _client = None
