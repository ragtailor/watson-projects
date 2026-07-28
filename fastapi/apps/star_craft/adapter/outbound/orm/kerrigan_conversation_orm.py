from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.matrix.grid_neo_theone_base import Base


class KerriganConversationOrm(Base):

    __tablename__ = "star_craft_kerrigan_conversation_turns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, index=True)
    message: Mapped[str] = mapped_column(Text)
    intent: Mapped[str] = mapped_column(String)
    reply: Mapped[str] = mapped_column(Text)
