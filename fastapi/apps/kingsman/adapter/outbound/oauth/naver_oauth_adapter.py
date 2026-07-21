from __future__ import annotations

from urllib.parse import urlencode

import httpx

from kingsman.app.dtos.oauth_dto import OAuthProfile
from kingsman.app.ports.output.oauth_provider_port import OAuthProviderPort

_AUTHORIZE_URL = "https://nid.naver.com/oauth2.0/authorize"
_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
_USERINFO_URL = "https://openapi.naver.com/v1/nid/me"


class NaverOAuthAdapter(OAuthProviderPort):

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret

    def build_authorize_url(self, state: str, redirect_uri: str, code_challenge: str | None = None) -> str:
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "state": state,
        }
        return f"{_AUTHORIZE_URL}?{urlencode(params)}"

    async def fetch_profile(self, code: str, redirect_uri: str, code_verifier: str | None = None) -> OAuthProfile:
        async with httpx.AsyncClient(timeout=10) as client:
            token_res = await client.get(
                _TOKEN_URL,
                params={
                    "grant_type": "authorization_code",
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "code": code,
                },
            )
            token_res.raise_for_status()
            access_token = token_res.json()["access_token"]

            profile_res = await client.get(
                _USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
            )
            profile_res.raise_for_status()
            data = profile_res.json().get("response", {})

        return OAuthProfile(
            provider="naver",
            subject=str(data.get("id", "")),
            email=data.get("email", ""),
            nickname=data.get("nickname", ""),
        )
