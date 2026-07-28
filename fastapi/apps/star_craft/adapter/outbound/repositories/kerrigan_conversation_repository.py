from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from star_craft.adapter.outbound.orm.kerrigan_conversation_orm import KerriganConversationOrm
from star_craft.app.ports.output.kerrigan_conversation_repository_port import (
    KerriganConversationRepositoryPort,
)

logger = logging.getLogger(__name__)


class KerriganConversationRepository(KerriganConversationRepositoryPort):
    """KerriganConversationRepositoryPort 구현."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_turn(self, session_id: str, message: str, intent: str, reply: str) -> None:
        logger.info(
            f"[KerriganConversationRepository] save_turn 진입 | "
            f"session_id={session_id} intent={intent}"
        )
        orm = KerriganConversationOrm(
            session_id=session_id,
            message=message,
            intent=intent,
            reply=reply,
        )
        self.session.add(orm)
        await self.session.commit()
