from __future__ import annotations

from urllib.parse import urlencode

import httpx

from kingsman.app.dtos.oauth_dto import OAuthProfile
from kingsman.app.ports.output.oauth_provider_port import OAuthProviderPort

_AUTHORIZE_URL = "https://twitter.com/i/oauth2/authorize"
_TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
_USERINFO_URL = "https://api.twitter.com/2/users/me"


class XOAuthAdapter(OAuthProviderPort):
    """X(Twitter) OAuth 2.0 + PKCE. 기본 스코프로는 이메일을 제공하지 않는다."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret

    def build_authorize_url(self, state: str, redirect_uri: str, code_challenge: str | None = None) -> str:
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "scope": "tweet.read users.read",
            "state": state,
            "code_challenge": code_challenge or "",
            "code_challenge_method": "S256",
        }
        return f"{_AUTHORIZE_URL}?{urlencode(params)}"

    async def fetch_profile(self, code: str, redirect_uri: str, code_verifier: str | None = None) -> OAuthProfile:
        async with httpx.AsyncClient(timeout=10) as client:
            token_res = await client.post(
                _TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "code_verifier": code_verifier or "",
                    "client_id": self._client_id,
                },
                auth=(self._client_id, self._client_secret),
            )
            token_res.raise_for_status()
            access_token = token_res.json()["access_token"]

            profile_res = await client.get(
                _USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
            )
            profile_res.raise_for_status()
            data = profile_res.json().get("data", {})

        return OAuthProfile(
            provider="x",
            subject=str(data.get("id", "")),
            email="",  # X 기본 스코프는 이메일을 제공하지 않는다.
            nickname=data.get("username", data.get("name", "")),
        )
