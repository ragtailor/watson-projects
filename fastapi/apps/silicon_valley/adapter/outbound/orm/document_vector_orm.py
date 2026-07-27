from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.matrix.grid_neo_theone_base import Base


class DocumentVectorOrm(Base):

    __tablename__ = "silicon_valley_document_vectors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[str] = mapped_column(Text)
