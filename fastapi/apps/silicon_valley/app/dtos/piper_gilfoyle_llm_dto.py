from dataclasses import dataclass

@dataclass(frozen=True)
class GilfoyleLlmQuery:

    prompt: str
    max_new_tokens: int
    temperature: float


@dataclass(frozen=True)
class GilfoyleLlmResponse:

    response: str
