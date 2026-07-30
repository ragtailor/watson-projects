from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from silicon_valley.adapter.outbound.orm.knowledge_chunk_orm import KnowledgeChunkOrm
from silicon_valley.app.ports.output.knowledge_chunk_repository_port import KnowledgeChunkRepositoryPort
from silicon_valley.domain.knowledge_chunk import KnowledgeChunk


class KnowledgeChunkRepository(KnowledgeChunkRepositoryPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_all(
        self,
        document_id: int,
        contents: list[str],
        embeddings: list[list[float]],
    ) -> int:
        if len(contents) != len(embeddings):
            raise ValueError(
                f"조각 수({len(contents)})와 임베딩 수({len(embeddings)})가 일치하지 않습니다."
            )

        orms = [
            KnowledgeChunkOrm(
                document_id=document_id,
                chunk_index=index,
                content=content,
                embedding=embedding,
            )
            for index, (content, embedding) in enumerate(zip(contents, embeddings))
        ]
        self.session.add_all(orms)
        await self.session.commit()

        return len(orms)

    async def search_similar(self, embedding: list[float], limit: int) -> list[KnowledgeChunk]:
        stmt = (
            select(KnowledgeChunkOrm)
            .order_by(KnowledgeChunkOrm.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        result = await self.session.execute(stmt)

        return [
            KnowledgeChunk(
                id=orm.id,
                document_id=orm.document_id,
                chunk_index=orm.chunk_index,
                content=orm.content,
            )
            for orm in result.scalars().all()
        ]
