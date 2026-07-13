from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from tailor.core.matrix.grid_neo_theone_base import Base


class StadiumOrm(Base):
    __tablename__ = "stadium"

    stadium_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    # 주의: ERD에 표기된 스펠링 오타를 그대로 유지
    statdium_name: Mapped[str] = mapped_column(String(40), nullable=False)
    hometeam_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    seat_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    address: Mapped[str | None] = mapped_column(String(60), nullable=True)
    ddd: Mapped[str | None] = mapped_column(String(10), nullable=True)
    tel: Mapped[str | None] = mapped_column(String(10), nullable=True)
