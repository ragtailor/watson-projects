from __future__ import annotations

import uuid

# 허용 이미지 타입. 클라이언트가 보낸 Content-Type을 그대로 믿지 않고 이 목록으로 거른다.
ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}

MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB

_DEFAULT_PREFIX = "silicon-valley/images"


class InvalidImageError(Exception):
    '''업로드된 이미지가 정책을 벗어남. 호출자 잘못이므로 4xx로 이어진다.'''


class ImageStorageError(Exception):
    '''저장소(S3) 쪽 실패. 요청 자체는 정상이므로 4xx와 구분한다.'''


def validate(content_type: str, size_bytes: int) -> None:
    '''업로드 정책 검증. 통과하지 못하면 InvalidImageError를 던진다.'''

    if size_bytes <= 0:
        raise InvalidImageError("빈 파일입니다.")
    if size_bytes > MAX_IMAGE_BYTES:
        raise InvalidImageError(
            f"이미지가 너무 큽니다. 최대 {MAX_IMAGE_BYTES // (1024 * 1024)}MB까지 업로드할 수 있습니다."
        )
    if content_type not in ALLOWED_CONTENT_TYPES:
        allowed = ", ".join(sorted(ALLOWED_CONTENT_TYPES))
        raise InvalidImageError(f"지원하지 않는 이미지 형식입니다. 허용: {allowed}")


def build_object_key(content_type: str, prefix: str = _DEFAULT_PREFIX) -> str:
    '''S3 오브젝트 키를 만든다.

    확장자를 원본 파일명이 아니라 검증된 Content-Type에서 끌어낸다.
    파일명은 사용자 입력이라 `../`나 실제 내용과 다른 확장자가 섞여 들어올 수 있다.
    이름 충돌과 열거(enumeration)를 막기 위해 uuid를 쓴다.
    '''
    extension = ALLOWED_CONTENT_TYPES[content_type]
    return f"{prefix}/{uuid.uuid4().hex}.{extension}"
