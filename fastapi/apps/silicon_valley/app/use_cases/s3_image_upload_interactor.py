from __future__ import annotations

import logging

from silicon_valley.app.dtos.s3_image_upload_dto import S3ImageUploadCommand, S3ImageUploadResponse
from silicon_valley.app.ports.input.s3_image_upload_use_case import S3ImageUploadUseCase
from silicon_valley.app.ports.output.image_storage_port import ImageStoragePort
from silicon_valley.domain.image_upload import build_object_key, validate

logger = logging.getLogger(__name__)


class S3ImageUploadInteractor(S3ImageUploadUseCase):

    def __init__(self, storage: ImageStoragePort):
        self.storage = storage

    async def upload(self, command: S3ImageUploadCommand) -> S3ImageUploadResponse:
        '''이미지 업로드 파이프라인: 정책 검증 → 오브젝트 키 생성 → 저장'''

        size_bytes = len(command.file_bytes)
        validate(command.content_type, size_bytes)

        key = build_object_key(command.content_type)
        url = await self.storage.save(key, command.content_type, command.file_bytes)

        logger.info(
            "[S3ImageUploadInteractor] 업로드 완료 | filename=%s key=%s size=%d",
            command.filename, key, size_bytes,
        )

        return S3ImageUploadResponse(
            key=key,
            url=url,
            size_bytes=size_bytes,
            content_type=command.content_type,
        )
