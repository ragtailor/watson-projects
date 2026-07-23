import base64
import binascii
import os

from dotenv import load_dotenv

load_dotenv()

# 예: postgresql+psycopg://user:password@localhost:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL")

# 이 백엔드가 검증 시 요구하는 토큰 audience.
# auth 컨테이너가 발급한 access token의 aud가 이 값과 일치해야만 통과한다.
# 실배포 도메인(api.ragtaylor.com) 기준의 식별자다.
SERVICE_AUD = os.getenv("SERVICE_AUD", "ragtaylor-api")


def _decode_key_material(raw: str) -> str:
    """PEM 키를 환경변수에서 읽는다.

    PEM은 여러 줄이라 환경변수 주입이 까다로우므로 두 가지 형태를 모두 허용한다.
    - PEM 원문(여러 줄) 그대로
    - base64로 한 줄로 인코딩한 형태 (docker/compose 주입에 유리)
    """
    raw = raw.strip()
    if "-----BEGIN" in raw:
        return raw
    try:
        return base64.b64decode(raw).decode("utf-8")
    except (binascii.Error, ValueError) as exc:
        raise RuntimeError(
            "JWT 키를 해석할 수 없습니다. PEM 원문 또는 base64 인코딩된 PEM이어야 합니다."
        ) from exc


def get_jwt_private_key() -> str:
    """개인키를 반환한다. 발급(auth 컨테이너) 경로에서만 호출해야 한다.

    호출 시점에 환경변수를 읽으므로, 개인키가 없는 백엔드 컨테이너에서도
    모듈 import 자체는 실패하지 않는다.
    """
    raw = os.getenv("JWT_PRIVATE_KEY")
    if not raw:
        raise RuntimeError(
            "JWT_PRIVATE_KEY가 설정되지 않았습니다. 토큰 발급은 auth 컨테이너에서만 가능합니다."
        )
    return _decode_key_material(raw)


def get_jwt_public_key() -> str:
    """공개키를 반환한다. 모든 컨테이너의 검증 경로에서 사용한다."""
    raw = os.getenv("JWT_PUBLIC_KEY")
    if not raw:
        raise RuntimeError("JWT_PUBLIC_KEY가 설정되지 않았습니다.")
    return _decode_key_material(raw)
