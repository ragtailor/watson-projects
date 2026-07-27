from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentVector:

    id: int | None
    filename: str
    content: str
    summary: str
