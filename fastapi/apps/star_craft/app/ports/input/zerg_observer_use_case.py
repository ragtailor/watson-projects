from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.zerg_observer_dto import ClassifyImageQuery, ClassifyImageResponse


class ZergObserverUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/vision_router.py 와 대응 (ConvNeXt Nano 이미지 분류)."""

    @abstractmethod
    async def classify_image(self, query: ClassifyImageQuery) -> ClassifyImageResponse:
        """업로드된 이미지를 분류하여 최상위 라벨과 top-k 신뢰도를 반환한다."""
        pass
