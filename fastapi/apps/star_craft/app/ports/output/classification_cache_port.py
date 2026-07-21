from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.zerg_observer_dto import ClassifyImageResponse


class ClassificationCachePort(ABC):

    @abstractmethod
    async def get(self, image_hash: str) -> ClassifyImageResponse | None:
        """이미지 해시로 캐시된 분류 결과를 조회한다. 없으면 None."""
        pass

    @abstractmethod
    async def set(self, image_hash: str, response: ClassifyImageResponse) -> None:
        """분류 결과를 TTL과 함께 캐시에 저장한다."""
        pass
