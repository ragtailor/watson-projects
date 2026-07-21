from dataclasses import dataclass


@dataclass
class OAuthUserEntity:

    id: int | None
    user_id: str
    nickname: str
    email: str
    oauth_provider: str
    oauth_subject: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OAuthUserEntity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
