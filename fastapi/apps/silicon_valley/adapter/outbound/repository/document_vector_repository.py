from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from silicon_valley.adapter.outbound.orm.document_vector_orm import DocumentVectorOrm
from silicon_valley.app.ports.output.graph_document_vector_port import GraphDocumentVectorPort
from silicon_valley.domain.document_vector import DocumentVector


class DocumentVectorRepository(GraphDocumentVectorPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, filename: str, content: str, summary: str) -> DocumentVector:
        orm = DocumentVectorOrm(filename=filename, content=content, summary=summary)
        self.session.add(orm)
        await self.session.commit()
        await self.session.refresh(orm)

        return DocumentVector(
            id=orm.id,
            filename=orm.filename,
            content=orm.content,
            summary=orm.summary,
        )
