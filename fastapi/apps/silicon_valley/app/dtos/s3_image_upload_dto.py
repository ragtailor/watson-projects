from dataclasses import dataclass


@dataclass(frozen=True)
class S3ImageUploadCommand:

    filename: str
    content_type: str
    file_bytes: bytes


@dataclass(frozen=True)
class S3ImageUploadResponse:

    key: str
    url: str
    size_bytes: int
    content_type: str
