from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.matrix.grid_neo_theone_base import Base

# nomic-embed-text의 실측 출력 차원. 임베딩 모델을 바꾸면 이 값과 마이그레이션을 함께 고쳐야 한다.
EMBEDDING_DIM = 768


class KnowledgeChunkOrm(Base):
    '''문서 조각 + 임베딩. 원문 1행 = document_vectors, 검색 단위 = 이 테이블.'''

    __tablename__ = "silicon_valley_document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("silicon_valley_document_vectors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
