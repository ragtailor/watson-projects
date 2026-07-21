from __future__ import annotations

import json

from redis.asyncio import Redis

from star_craft.app.dtos.zerg_observer_dto import ClassifyImageResponse, LabelScore
from star_craft.app.ports.output.classification_cache_port import ClassificationCachePort

_KEY_PREFIX = "zerg-observer:classify:"


class RedisClassificationCacheAdapter(ClassificationCachePort):
    """이미지 해시(sha256) 기준으로 분류 결과를 totem(Redis)에 캐싱한다."""

    def __init__(self, client: Redis, ttl_seconds: int) -> None:
        self._client = client
        self._ttl_seconds = ttl_seconds

    async def get(self, image_hash: str) -> ClassifyImageResponse | None:
        raw = await self._client.get(_KEY_PREFIX + image_hash)
        if raw is None:
            return None

        payload = json.loads(raw)
        return ClassifyImageResponse(
            label=payload["label"],
            confidence=payload["confidence"],
            top5=[LabelScore(**item) for item in payload["top5"]],
        )

    async def set(self, image_hash: str, response: ClassifyImageResponse) -> None:
        payload = {
            "label": response.label,
            "confidence": response.confidence,
            "top5": [{"label": s.label, "confidence": s.confidence} for s in response.top5],
        }
        await self._client.set(_KEY_PREFIX + image_hash, json.dumps(payload), ex=self._ttl_seconds)
