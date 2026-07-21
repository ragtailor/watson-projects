import pytest

from kingsman.app.dtos.oauth_dto import OAuthLoginResult, OAuthProfile
from kingsman.app.use_cases.oauth_login_interactor import OAuthLoginInteractor


class _FakeUserRepository:
    def __init__(self) -> None:
        self.by_oauth: dict[tuple[str, str], OAuthLoginResult] = {}
        self.upsert_calls = 0

    async def find_by_oauth(self, provider: str, subject: str) -> OAuthLoginResult | None:
        return self.by_oauth.get((provider, subject))

    async def upsert_oauth_user(self, profile: OAuthProfile) -> OAuthLoginResult:
        self.upsert_calls += 1
        result = OAuthLoginResult(
            user_id=f"{profile.provider}_{profile.subject}",
            nickname=profile.nickname,
            email=profile.email,
        )
        self.by_oauth[(profile.provider, profile.subject)] = result
        return result


def _make_profile(provider: str = "google", subject: str = "12345") -> OAuthProfile:
    return OAuthProfile(provider=provider, subject=subject, email="a@b.com", nickname="ragtailor")


@pytest.mark.asyncio
async def test_login_with_profile_creates_new_user_on_first_login():
    repo = _FakeUserRepository()
    interactor = OAuthLoginInteractor(users=repo)

    result = await interactor.login_with_profile(_make_profile())

    assert result.user_id == "google_12345"
    assert result.nickname == "ragtailor"
    assert repo.upsert_calls == 1


@pytest.mark.asyncio
async def test_login_with_profile_reuses_existing_user_without_upsert():
    repo = _FakeUserRepository()
    interactor = OAuthLoginInteractor(users=repo)
    profile = _make_profile()

    first = await interactor.login_with_profile(profile)
    second = await interactor.login_with_profile(profile)

    assert first == second
    assert repo.upsert_calls == 1  # 두 번째 로그인은 기존 사용자를 그대로 재사용


@pytest.mark.asyncio
async def test_login_with_profile_distinguishes_providers_with_same_subject():
    repo = _FakeUserRepository()
    interactor = OAuthLoginInteractor(users=repo)

    google_result = await interactor.login_with_profile(_make_profile(provider="google", subject="1"))
    naver_result = await interactor.login_with_profile(_make_profile(provider="naver", subject="1"))

    assert google_result.user_id != naver_result.user_id
    assert repo.upsert_calls == 2
