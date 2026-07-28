from dataclasses import dataclass


@dataclass(frozen=True)
class KerriganChatCommand:

    session_id: str
    message: str


@dataclass(frozen=True)
class KerriganChatResponse:

    session_id: str
    intent: str
    reply: str
