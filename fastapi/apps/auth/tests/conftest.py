import os
import sys
from pathlib import Path

_here = Path(__file__).parent
_apps_dir = str(_here.parent.parent)        # fastapi/apps/ → "auth.*" 임포트
_root_dir = str(_here.parent.parent.parent)  # fastapi/       → "core.*" 임포트
for _p in (_apps_dir, _root_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@pytest.fixture(scope="session", autouse=True)
def _jwt_keys():
    """테스트용 RS256 키쌍을 생성해 환경변수로 주입한다(DB/Redis 불필요)."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    os.environ["JWT_PRIVATE_KEY"] = private_pem
    os.environ["JWT_PUBLIC_KEY"] = public_pem
    yield
