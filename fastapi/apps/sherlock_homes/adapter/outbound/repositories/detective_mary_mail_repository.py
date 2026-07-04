from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from sherlock_homes.adapter.outbound.orm.detective_mary_mail_orm import MaryMailOrm
from sherlock_homes.app.dtos.detective_mary_mail_dto import MaryMailQuery, MaryMailResponse, MaryMailReceiveQuery, MaryMailReceiveResponse
from sherlock_homes.app.ports.output.detective_mary_mail_port import MaryMailPort

logger = logging.getLogger(__name__)


class MaryMailRepository(MaryMailPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: MaryMailQuery) -> MaryMailResponse:
        '''메리 왓슨의 자기소개'''
        logger.info(f"[MaryMailRepository] introduce_myself | id={query.id} name={query.name}")
        return MaryMailResponse(
            id=query.id,
            name=query.name,
        )

    async def receive_mail(self, query: MaryMailReceiveQuery) -> MaryMailReceiveResponse:
        '''n8n으로부터 수신한 Gmail 메일을 임베딩과 함께 pgvector에 저장'''
        logger.info(
            f"[MaryMailRepository] receive_mail | "
            f"message_id={query.message_id} subject={query.subject} from={query.from_}"
        )

        self.session.add(MaryMailOrm(
            message_id=query.message_id,
            subject=query.subject,
            from_=query.from_,
            to=query.to,
            preview=query.preview,
            embedding=query.embedding,
        ))
        await self.session.commit()

        return MaryMailReceiveResponse(
            message_id=query.message_id,
            status="received",
        )
