from __future__ import annotations

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from core.matrix.grid_neo_theone_base import Base


class UserOrm(Base):

    __tablename__ = "kingsman_users"
    __table_args__ = (
        UniqueConstraint("oauth_provider", "oauth_subject", name="uq_kingsman_users_oauth"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, unique=True)
    nickname: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    oauth_provider: Mapped[str] = mapped_column(String)
    oauth_subject: Mapped[str] = mapped_column(String)
