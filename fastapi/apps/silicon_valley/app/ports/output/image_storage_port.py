from __future__ import annotations

from abc import ABC, abstractmethod


class ImageStoragePort(ABC):

    @abstractmethod
    async def save(self, key: str, content_type: str, data: bytes) -> str:
        '''주어진 키로 이미지를 저장하고 접근 가능한 URL을 반환한다.

        키 생성은 앱(도메인) 정책이므로 구현체가 만들지 않는다. 구현체는 받은 키를 그대로 쓴다.
        실패는 domain.image_upload.ImageStorageError로 올린다 — 라우터가 boto3 예외를 알 필요는 없다.
        '''
        pass
