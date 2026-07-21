import os

from core.matrix.totem_redis_cache_manager import get_client
from star_craft.adapter.outbound.caches.redis_classification_cache_adapter import (
    RedisClassificationCacheAdapter,
)
from star_craft.adapter.outbound.resource_adapters.convnext.convnext_image_classifier_adapter import (
    ConvNextImageClassifierAdapter,
)
from star_craft.app.ports.input.zerg_observer_use_case import ZergObserverUseCase
from star_craft.app.ports.output.classification_cache_port import ClassificationCachePort
from star_craft.app.ports.output.image_classifier_port import ImageClassifierPort
from star_craft.app.use_cases.zerg_observer_image_classifier_interactor import (
    ZergObserverImageClassifierInteractor,
)

_MODEL_NAME = os.getenv("ZERG_OBSERVER_MODEL_NAME", "convnext_nano")
_BACKEND = os.getenv("INFERENCE_BACKEND", "onnx")
_DEFAULT_ONNX_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "resources", "models", "convnext_nano_int8.onnx"
)
_ONNX_MODEL_PATH = os.getenv("ZERG_OBSERVER_ONNX_PATH", _DEFAULT_ONNX_PATH)
_MAX_IMAGE_BYTES = int(os.getenv("ZERG_OBSERVER_MAX_IMAGE_BYTES", str(10 * 1024 * 1024)))
_CACHE_TTL_SECONDS = int(os.getenv("ZERG_OBSERVER_CACHE_TTL_SECONDS", "3600"))

# 모델 로드(가중치 다운로드/ONNX 변환) 비용이 크므로 프로세스당 한 번만 생성해 재사용한다.
_classifier_singleton: ImageClassifierPort | None = None


def get_image_classifier_port() -> ImageClassifierPort:
    global _classifier_singleton
    if _classifier_singleton is None:
        _classifier_singleton = ConvNextImageClassifierAdapter(
            model_name=_MODEL_NAME,
            onnx_model_path=_ONNX_MODEL_PATH,
            backend=_BACKEND,
        )
    return _classifier_singleton


def get_classification_cache_port() -> ClassificationCachePort:
    return RedisClassificationCacheAdapter(client=get_client(), ttl_seconds=_CACHE_TTL_SECONDS)


def get_zerg_observer_use_case() -> ZergObserverUseCase:
    return ZergObserverImageClassifierInteractor(
        classifier=get_image_classifier_port(),
        cache=get_classification_cache_port(),
        max_image_bytes=_MAX_IMAGE_BYTES,
    )
