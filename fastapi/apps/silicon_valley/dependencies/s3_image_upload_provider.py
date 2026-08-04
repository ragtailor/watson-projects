import os

from fastapi import Depends

from silicon_valley.adapter.outbound.s3.s3_image_storage_adapter import S3ImageStorageAdapter
from silicon_valley.app.ports.input.s3_image_upload_use_case import S3ImageUploadUseCase
from silicon_valley.app.ports.output.image_storage_port import ImageStoragePort
from silicon_valley.app.use_cases.s3_image_upload_interactor import S3ImageUploadInteractor

# 버킷 "이름"이다. ARN(arn:aws:s3:::taylor-bucket-10498)이 아니라 마지막 조각만 넣는다.
_S3_BUCKET = os.getenv("S3_BUCKET", "")

"""
S3 이미지 업로드 의존성 조립소 (DIP 팩토리).

  - 라우터는 구현체(S3ImageStorageAdapter)를 알지 못하고 포트(S3ImageUploadUseCase)만 본다.
  - 버킷 같은 인프라 설정은 이 조립소에서만 읽는다.
"""


def get_image_storage() -> ImageStoragePort:
    return S3ImageStorageAdapter(bucket=_S3_BUCKET)


def get_s3_image_upload_use_case(
    storage: ImageStoragePort = Depends(get_image_storage),
) -> S3ImageUploadUseCase:

    return S3ImageUploadInteractor(storage=storage)
