from __future__ import annotations

from abc import ABC, abstractmethod


class UserSessionPort(ABC):
    """로그인한 사용자의 세션 토큰 발급/검증을 담당하는 출력 포트."""

    @abstractmethod
    def issue(self, user_id: str) -> str:
        """user_id를 담은 서명된 세션 토큰을 발급한다."""
        pass

    @abstractmethod
    def verify(self, token: str) -> str | None:
        """세션 토큰을 검증해 user_id를 반환한다. 유효하지 않으면 None."""
        pass
