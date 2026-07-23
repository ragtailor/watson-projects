"""RBAC 정의 — 역할, 권한, 역할→권한 매핑, OAuth 프로바이더.

Role은 core.security에 정의된 정본을 재노출한다(백엔드와 공용이어야 하며,
core가 apps.auth를 import하면 안 되기 때문에 정의 위치가 core다).
Permission과 매핑 테이블, 지원 프로바이더 목록은 auth 도메인 소유다.
"""

from __future__ import annotations

from enum import StrEnum

from core.security import Role

__all__ = ["Role", "Permission", "ROLE_PERMISSIONS", "permissions_for", "Provider"]


class Permission(StrEnum):
    READ = "read"
    WRITE = "write"
    MANAGE_USERS = "manage_users"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.MANAGE_USERS},
    Role.USER: {Permission.READ, Permission.WRITE},
}


def permissions_for(roles: list[str]) -> set[Permission]:
    granted: set[Permission] = set()
    for raw in roles:
        try:
            role = Role(raw)
        except ValueError:
            continue
        granted |= ROLE_PERMISSIONS.get(role, set())
    return granted


class Provider(StrEnum):
    """지원하는 소셜 로그인 프로바이더(kingsman과 동일 집합)."""

    GOOGLE = "google"
    KAKAO = "kakao"
    NAVER = "naver"
    X = "x"
