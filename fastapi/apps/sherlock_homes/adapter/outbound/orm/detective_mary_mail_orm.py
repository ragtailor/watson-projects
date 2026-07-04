from __future__ import annotations

from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from tailor.core.matrix.grid_neo_theone_base import Base

EMBEDDING_DIM = 1024


class MaryMailOrm(Base):

    __tablename__ = "mary_mail_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str | None] = mapped_column(String, nullable=True)
    from_: Mapped[str | None] = mapped_column("from", String, nullable=True)
    to: Mapped[str | None] = mapped_column(String, nullable=True)
    preview: Mapped[str | None] = mapped_column(String, nullable=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
