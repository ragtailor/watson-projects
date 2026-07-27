from dataclasses import dataclass


@dataclass(frozen=True)
class MorningstarInsightCommand:

    question: str
    report_limit: int = 5


@dataclass(frozen=True)
class MorningstarInsightResponse:

    question: str
    insight: str
    sources: list[str]
