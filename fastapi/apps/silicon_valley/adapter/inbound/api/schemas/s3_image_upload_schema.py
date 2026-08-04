from pydantic import BaseModel, Field


class S3ImageUploadResultSchema(BaseModel):

    key: str = Field(..., description="S3 오브젝트 키")
    url: str = Field(..., description="업로드된 이미지의 접근 URL")
    size_bytes: int = Field(..., description="업로드된 이미지 크기(바이트)")
    content_type: str = Field(..., description="검증된 이미지 MIME 타입")
