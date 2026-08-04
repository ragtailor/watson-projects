from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from silicon_valley.adapter.inbound.api.schemas.s3_image_upload_schema import S3ImageUploadResultSchema
from silicon_valley.app.dtos.s3_image_upload_dto import S3ImageUploadCommand
from silicon_valley.app.ports.input.s3_image_upload_use_case import S3ImageUploadUseCase
from silicon_valley.dependencies.s3_image_upload_provider import get_s3_image_upload_use_case
from silicon_valley.domain.image_upload import ImageStorageError, InvalidImageError

'''
이미지 업로드 → S3 저장 라우터.

이 계층은 HTTP만 담당한다 — 멀티파트를 커맨드로 바꾸고, 앱 계층의 예외를 상태 코드로 옮긴다.
검증 정책과 키 규칙은 domain/image_upload.py, 저장은 outbound 어댑터에 있다.
'''
s3_image_upload_router = APIRouter(prefix="/images", tags=["images"])


@s3_image_upload_router.post(
    "/upload",
    response_model=S3ImageUploadResultSchema,
    status_code=status.HTTP_201_CREATED,
    summary="이미지 업로드 후 S3 저장",
)
async def upload_image(
    file: UploadFile = File(...),
    use_case: S3ImageUploadUseCase = Depends(get_s3_image_upload_use_case),
) -> S3ImageUploadResultSchema:

    file_bytes = await file.read()

    try:
        response = await use_case.upload(
            S3ImageUploadCommand(
                filename=file.filename or "",
                content_type=file.content_type or "",
                file_bytes=file_bytes,
            )
        )
    except InvalidImageError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ImageStorageError as exc:
        # 요청은 정상인데 저장소가 실패한 경우다. 클라이언트 잘못으로 표시하지 않는다.
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    return S3ImageUploadResultSchema(
        key=response.key,
        url=response.url,
        size_bytes=response.size_bytes,
        content_type=response.content_type,
    )
