from __future__ import annotations

import boto3
from botocore.client import BaseClient

from core.matrix.vault_keymaker_secret_manager import get_keymaker

_client: BaseClient | None = None


def init_client() -> None:
    global _client
    if _client is not None:
        return

    keymaker = get_keymaker()
    access_key = keymaker.get_secret("AWS_ACCESS_KEY_ID")
    secret_key = keymaker.get_secret("AWS_SECRET_ACCESS_KEY")
    if not access_key or not secret_key:
        return

    _client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=keymaker.get_secret("AWS_DEFAULT_REGION"),
    )


def get_client() -> BaseClient:
    if _client is None:
        init_client()

    if _client is None:
        raise RuntimeError(
            "AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY가 설정되지 않아 S3 클라이언트를 초기화할 수 없습니다."
        )

    return _client


def list_bucket_names() -> list[str]:
    response = get_client().list_buckets()
    return [bucket["Name"] for bucket in response["Buckets"]]
