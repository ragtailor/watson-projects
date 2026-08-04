from __future__ import annotations

import asyncio
import logging

from botocore.exceptions import BotoCoreError, ClientError

from core.matrix.aws_tank_s3_manager import get_client
from silicon_valley.app.ports.output.image_storage_port import ImageStoragePort
from silicon_valley.domain.image_upload import ImageStorageError

logger = logging.getLogger(__name__)


class S3ImageStorageAdapter(ImageStoragePort):
    '''AWS S3에 이미지를 저장하는 어댑터.

    클라이언트는 core.matrix.aws_tank_s3_manager의 공용 인스턴스를 쓴다.
    자격증명(.env의 AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_DEFAULT_REGION)이
    한 곳에서만 해석되도록 하기 위함이다.
    '''

    def __init__(self, bucket: str) -> None:
        self._bucket = bucket

    async def save(self, key: str, content_type: str, data: bytes) -> str:
        if not self._bucket:
            raise ImageStorageError("S3 버킷이 설정되지 않았습니다. S3_BUCKET 환경변수를 확인하세요.")

        # boto3는 동기 블로킹 I/O다. 이벤트 루프를 막지 않도록 스레드로 넘긴다.
        return await asyncio.to_thread(self._save_sync, key, content_type, data)

    def _save_sync(self, key: str, content_type: str, data: bytes) -> str:
        try:
            client = get_client()
            client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
        except (BotoCoreError, ClientError, RuntimeError) as exc:
            # boto3 예외를 그대로 올리면 상위 계층이 AWS SDK를 알게 된다.
            logger.exception("[S3ImageStorageAdapter] 업로드 실패 | bucket=%s key=%s", self._bucket, key)
            raise ImageStorageError(f"S3 업로드에 실패했습니다: {exc}") from exc

        region = client.meta.region_name
        logger.info("[S3ImageStorageAdapter] 업로드 완료 → s3://%s/%s", self._bucket, key)
        return f"https://{self._bucket}.s3.{region}.amazonaws.com/{key}"
