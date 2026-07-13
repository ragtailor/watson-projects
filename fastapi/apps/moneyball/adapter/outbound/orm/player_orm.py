from __future__ import annotations

from datetime import date

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from tailor.core.matrix.grid_neo_theone_base import Base


class PlayerOrm(Base):
    __tablename__ = "player"

    player_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    player_name: Mapped[str] = mapped_column(String(20), nullable=False)
    e_player_name: Mapped[str | None] = mapped_column(String(40), nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(30), nullable=True)
    join_yyyy: Mapped[str | None] = mapped_column(String(10), nullable=True)
    position: Mapped[str | None] = mapped_column(String(10), nullable=True)
    back_no: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nation: Mapped[str | None] = mapped_column(String(20), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    solar: Mapped[str | None] = mapped_column(String(10), nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight: Mapped[int | None] = mapped_column(Integer, nullable=True)
    team_id: Mapped[str | None] = mapped_column(
        String(10), ForeignKey("team.team_id"), nullable=True
    )
    # OpenAI text-embedding-3-small 등 표준 임베딩 모델 규격(1536차원)
    player_embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
