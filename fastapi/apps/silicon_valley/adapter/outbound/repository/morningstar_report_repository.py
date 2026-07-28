from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from silicon_valley.adapter.outbound.orm.document_vector_orm import DocumentVectorOrm
from silicon_valley.app.ports.output.morningstar_report_repository_port import MorningstarReportRepositoryPort
from silicon_valley.domain.document_vector import DocumentVector


class MorningstarReportRepository(MorningstarReportRepositoryPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_recent_reports(self, limit: int) -> list[DocumentVector]:
        stmt = (
            select(DocumentVectorOrm)
            .order_by(DocumentVectorOrm.id.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            DocumentVector(id=orm.id, filename=orm.filename, content=orm.content, summary=orm.summary)
            for orm in orms
        ]
