"""silicon_valley 문서 조각 + 임베딩 테이블 추가

Revision ID: a1c4f7e2b930
Revises: 31bfc4aabf96
Create Date: 2026-07-30

009-langgraph-strategy.md 2단계. 원문 1행은 기존 silicon_valley_document_vectors 에
그대로 두고, 검색 단위인 조각만 이 테이블에 분리해 적재한다.
차원 768은 nomic-embed-text 실측값이며 KnowledgeChunkOrm.EMBEDDING_DIM 과 일치해야 한다.
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "a1c4f7e2b930"
down_revision = "31bfc4aabf96"
branch_labels = None
depends_on = None

EMBEDDING_DIM = 768


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "silicon_valley_document_chunks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["silicon_valley_document_vectors.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_silicon_valley_document_chunks_document_id"),
        "silicon_valley_document_chunks",
        ["document_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_silicon_valley_document_chunks_document_id"),
        table_name="silicon_valley_document_chunks",
    )
    op.drop_table("silicon_valley_document_chunks")
