from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthProfile:
    """OAuth 프로바이더가 반환한 사용자 프로필 (인증 완료 후)."""

    provider: str
    subject: str  # 프로바이더 쪽 고유 사용자 ID (sub)
    email: str
    nickname: str


@dataclass(frozen=True)
class OAuthLoginResult:

    user_id: str
    nickname: str
    email: str
