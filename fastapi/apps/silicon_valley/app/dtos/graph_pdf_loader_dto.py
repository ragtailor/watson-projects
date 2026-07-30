from dataclasses import dataclass


@dataclass(frozen=True)
class GraphPdfLoaderCommand:

    filename: str
    file_bytes: bytes


@dataclass(frozen=True)
class GraphPdfLoaderResponse:

    id: int
    filename: str
    summary: str
    chunk_count: int
