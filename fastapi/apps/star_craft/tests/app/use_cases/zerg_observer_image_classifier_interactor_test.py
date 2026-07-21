import hashlib

import pytest

from star_craft.app.dtos.zerg_observer_dto import ClassifyImageQuery, ClassifyImageResponse, LabelScore
from star_craft.app.use_cases.zerg_observer_image_classifier_interactor import (
    ZergObserverImageClassifierInteractor,
)


class _FakeClassifier:
    def __init__(self, results: list[LabelScore]) -> None:
        self.results = results
        self.calls = 0

    def classify(self, image_data: bytes, top_k: int) -> list[LabelScore]:
        self.calls += 1
        return self.results[:top_k]


class _FakeCache:
    def __init__(self) -> None:
        self.store: dict[str, ClassifyImageResponse] = {}

    async def get(self, image_hash: str) -> ClassifyImageResponse | None:
        return self.store.get(image_hash)

    async def set(self, image_hash: str, response: ClassifyImageResponse) -> None:
        self.store[image_hash] = response


_SAMPLE_TOP5 = [
    LabelScore(label="tabby cat", confidence=0.91),
    LabelScore(label="tiger cat", confidence=0.05),
]


def _make_query(data: bytes = b"fake-image-bytes") -> ClassifyImageQuery:
    return ClassifyImageQuery(
        filename="cat.jpg",
        content_type="image/jpeg",
        size=len(data),
        data=data,
    )


@pytest.mark.asyncio
async def test_classify_image_returns_top1_and_caches_result():
    classifier = _FakeClassifier(_SAMPLE_TOP5)
    cache = _FakeCache()
    interactor = ZergObserverImageClassifierInteractor(
        classifier=classifier, cache=cache, max_image_bytes=1024
    )

    response = await interactor.classify_image(_make_query())

    assert response.label == "tabby cat"
    assert response.confidence == 0.91
    assert response.top5 == _SAMPLE_TOP5
    assert classifier.calls == 1

    image_hash = hashlib.sha256(b"fake-image-bytes").hexdigest()
    assert cache.store[image_hash] == response


@pytest.mark.asyncio
async def test_classify_image_uses_cache_and_skips_classifier():
    classifier = _FakeClassifier(_SAMPLE_TOP5)
    cache = _FakeCache()
    cached_response = ClassifyImageResponse(label="cached", confidence=0.99, top5=_SAMPLE_TOP5)
    image_hash = hashlib.sha256(b"fake-image-bytes").hexdigest()
    cache.store[image_hash] = cached_response

    interactor = ZergObserverImageClassifierInteractor(
        classifier=classifier, cache=cache, max_image_bytes=1024
    )

    response = await interactor.classify_image(_make_query())

    assert response is cached_response
    assert classifier.calls == 0


@pytest.mark.asyncio
async def test_classify_image_rejects_oversized_image():
    interactor = ZergObserverImageClassifierInteractor(
        classifier=_FakeClassifier(_SAMPLE_TOP5), cache=_FakeCache(), max_image_bytes=4
    )

    with pytest.raises(ValueError):
        await interactor.classify_image(_make_query(data=b"too-big"))


@pytest.mark.asyncio
async def test_classify_image_rejects_unsupported_content_type():
    interactor = ZergObserverImageClassifierInteractor(
        classifier=_FakeClassifier(_SAMPLE_TOP5), cache=_FakeCache(), max_image_bytes=1024
    )
    query = ClassifyImageQuery(filename="doc.gif", content_type="image/gif", size=3, data=b"gif")

    with pytest.raises(ValueError):
        await interactor.classify_image(query)
