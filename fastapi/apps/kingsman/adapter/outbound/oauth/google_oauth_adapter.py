from __future__ import annotations

from urllib.parse import urlencode

import httpx

from kingsman.app.dtos.oauth_dto import OAuthProfile
from kingsman.app.ports.output.oauth_provider_port import OAuthProviderPort

_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class GoogleOAuthAdapter(OAuthProviderPort):

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret

    def build_authorize_url(self, state: str, redirect_uri: str, code_challenge: str | None = None) -> str:
        params = {
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
        }
        return f"{_AUTHORIZE_URL}?{urlencode(params)}"

    async def fetch_profile(self, code: str, redirect_uri: str, code_verifier: str | None = None) -> OAuthProfile:
        async with httpx.AsyncClient(timeout=10) as client:
            token_res = await client.post(
                _TOKEN_URL,
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            token_res.raise_for_status()
            access_token = token_res.json()["access_token"]

            profile_res = await client.get(
                _USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
            )
            profile_res.raise_for_status()
            data = profile_res.json()

        return OAuthProfile(
            provider="google",
            subject=data["sub"],
            email=data.get("email", ""),
            nickname=data.get("name", ""),
        )
