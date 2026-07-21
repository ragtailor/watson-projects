from __future__ import annotations

from urllib.parse import urlencode

import httpx

from kingsman.app.dtos.oauth_dto import OAuthProfile
from kingsman.app.ports.output.oauth_provider_port import OAuthProviderPort

_AUTHORIZE_URL = "https://kauth.kakao.com/oauth/authorize"
_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
_USERINFO_URL = "https://kapi.kakao.com/v2/user/me"


class KakaoOAuthAdapter(OAuthProviderPort):

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret

    def build_authorize_url(self, state: str, redirect_uri: str, code_challenge: str | None = None) -> str:
        params = {
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
        }
        return f"{_AUTHORIZE_URL}?{urlencode(params)}"

    async def fetch_profile(self, code: str, redirect_uri: str, code_verifier: str | None = None) -> OAuthProfile:
        token_data = {
            "grant_type": "authorization_code",
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "code": code,
        }
        if self._client_secret:
            token_data["client_secret"] = self._client_secret

        async with httpx.AsyncClient(timeout=10) as client:
            token_res = await client.post(_TOKEN_URL, data=token_data)
            token_res.raise_for_status()
            access_token = token_res.json()["access_token"]

            profile_res = await client.get(
                _USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
            )
            profile_res.raise_for_status()
            data = profile_res.json()

        account = data.get("kakao_account", {})
        profile = account.get("profile", {})
        return OAuthProfile(
            provider="kakao",
            subject=str(data.get("id", "")),
            email=account.get("email", ""),
            nickname=profile.get("nickname", ""),
        )
