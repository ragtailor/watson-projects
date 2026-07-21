from __future__ import annotations

import asyncio
import hashlib

from star_craft.app.dtos.zerg_observer_dto import ClassifyImageQuery, ClassifyImageResponse
from star_craft.app.ports.input.zerg_observer_use_case import ZergObserverUseCase
from star_craft.app.ports.output.classification_cache_port import ClassificationCachePort
from star_craft.app.ports.output.image_classifier_port import ImageClassifierPort

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


class ZergObserverImageClassifierInteractor(ZergObserverUseCase):
    """ConvNeXt Nano 기반 이미지 분류 유스케이스."""

    def __init__(
        self,
        classifier: ImageClassifierPort,
        cache: ClassificationCachePort,
        max_image_bytes: int,
    ) -> None:
        self._classifier = classifier
        self._cache = cache
        self._max_image_bytes = max_image_bytes

    async def classify_image(self, query: ClassifyImageQuery) -> ClassifyImageResponse:
        self._validate(query)

        image_hash = hashlib.sha256(query.data).hexdigest()
        cached = await self._cache.get(image_hash)
        if cached is not None:
            return cached

        # ONNX/torch 추론은 CPU-bound이므로 스레드풀로 넘겨 이벤트 루프를 막지 않는다.
        top5 = await asyncio.to_thread(self._classifier.classify, query.data, query.top_k)
        best = top5[0]
        response = ClassifyImageResponse(label=best.label, confidence=best.confidence, top5=top5)

        await self._cache.set(image_hash, response)
        return response

    def _validate(self, query: ClassifyImageQuery) -> None:
        if query.content_type not in _ALLOWED_CONTENT_TYPES:
            raise ValueError(f"지원하지 않는 이미지 형식입니다: {query.content_type}")
        if query.size > self._max_image_bytes:
            raise ValueError(
                f"이미지 크기가 너무 큽니다: {query.size} bytes (최대 {self._max_image_bytes} bytes)"
            )
