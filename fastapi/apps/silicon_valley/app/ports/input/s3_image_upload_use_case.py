from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.s3_image_upload_dto import S3ImageUploadCommand, S3ImageUploadResponse


class S3ImageUploadUseCase(ABC):

    @abstractmethod
    async def upload(self, command: S3ImageUploadCommand) -> S3ImageUploadResponse:
        '''이미지를 검증한 뒤 오브젝트 스토리지에 저장하고 접근 URL을 돌려주는 메소드'''
        pass
