"""검증된 카카오 신원 → kingsman_users 조회/가입.

FAST-003 §9-2의 (a)안: auth가 kingsman_users에 직접 접근한다.
테이블에 UNIQUE(oauth_provider, oauth_subject)가 이미 있고, user_id 생성 규칙도
kingsman의 리포지터리를 그대로 재사용해 웹 로그인 경로와 일치시킨다.

세션 팩토리를 여기서 직접 만드는 이유: 공용 엔진(core.matrix.grid_oracle_database_manager)은
api 서비스가 lifespan에서 init_engine으로 띄운다. auth 컨테이너에는 그 lifespan이 없으므로
자기 엔진을 직접 만든다.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from auth.oidc.kakao_verifier import KakaoIdentity
from core import config

_PROVIDER = "kakao"

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _async_database_url() -> str:
    """DATABASE_URL을 async 드라이버 형태로 맞춘다.

    .env의 값이 `postgresql://...`(동기 드라이버)로 들어오는 경우가 있어
    async 엔진이 거부한다. 드라이버가 지정돼 있으면 그대로 쓴다.
    """
    url = config.DATABASE_URL
    if not url:
        raise RuntimeError("DATABASE_URL이 설정되지 않았습니다.")
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _factory() -> async_sessionmaker[AsyncSession]:
    global _engine, _session_factory
    if _session_factory is None:
        _engine = create_async_engine(_async_database_url(), pool_pre_ping=True)
        _session_factory = async_sessionmaker(bind=_engine, expire_on_commit=False, autoflush=False)
    return _session_factory


async def resolve_user(identity: KakaoIdentity) -> str:
    """카카오 sub로 사용자를 찾고, 없으면 가입시킨 뒤 user_id를 돌려준다.

    이 user_id가 자체 JWT의 sub가 된다.
    """
    from kingsman.adapter.outbound.repositories.user_repository import UserRepository
    from kingsman.app.dtos.oauth_dto import OAuthProfile

    async with _factory()() as session:
        repository = UserRepository(session)
        found = await repository.find_by_oauth(_PROVIDER, identity.sub)
        if found is not None:
            return found.user_id

        # 이메일·닉네임은 동의 항목이라 없을 수 있다. 없다고 가입을 막지 않는다.
        created = await repository.upsert_oauth_user(
            OAuthProfile(
                provider=_PROVIDER,
                subject=identity.sub,
                email=identity.email or "",
                nickname=identity.nickname or "",
            )
        )
        return created.user_id
