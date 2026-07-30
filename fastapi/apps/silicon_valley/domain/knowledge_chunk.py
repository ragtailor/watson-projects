from __future__ import annotations

from dataclasses import dataclass

_DEFAULT_CHUNK_SIZE = 800
_DEFAULT_OVERLAP = 100


@dataclass(frozen=True)
class KnowledgeChunk:
    '''문서를 검색 단위로 쪼갠 조각. 임베딩은 어댑터 계층에서만 다룬다.'''

    id: int | None
    document_id: int
    chunk_index: int
    content: str


def split_into_chunks(
    text: str,
    chunk_size: int = _DEFAULT_CHUNK_SIZE,
    overlap: int = _DEFAULT_OVERLAP,
) -> list[str]:
    '''본문을 겹침(overlap)을 둔 고정 길이 조각으로 나눈다.

    겹침을 두는 이유는 조각 경계에서 문맥이 끊겨 검색 품질이 떨어지는 것을 막기 위함이다.
    '''
    if chunk_size <= 0:
        raise ValueError("chunk_size는 1 이상이어야 합니다.")
    if overlap < 0:
        raise ValueError("overlap은 0 이상이어야 합니다.")
    if overlap >= chunk_size:
        raise ValueError("overlap은 chunk_size보다 작아야 합니다.")

    stripped = text.strip()
    if not stripped:
        return []

    step = chunk_size - overlap
    chunks = []
    for start in range(0, len(stripped), step):
        chunk = stripped[start:start + chunk_size]
        if chunk:
            chunks.append(chunk)
        if start + chunk_size >= len(stripped):
            break

    return chunks
