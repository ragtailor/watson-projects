from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.zerg_observer_dto import LabelScore


class ImageClassifierPort(ABC):

    @abstractmethod
    def classify(self, image_data: bytes, top_k: int) -> list[LabelScore]:
        """이미지 바이트를 추론하여 신뢰도 내림차순 top-k 라벨을 반환한다."""
        pass
