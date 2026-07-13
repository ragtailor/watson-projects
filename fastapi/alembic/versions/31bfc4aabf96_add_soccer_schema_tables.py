"""add soccer schema tables (stadium, team, schedule, player)

Revision ID: 31bfc4aabf96
Revises: 938ac8b2145d
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '31bfc4aabf96'
down_revision: Union[str, Sequence[str], None] = '938ac8b2145d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.create_table(
        'stadium',
        sa.Column('stadium_id', sa.String(length=10), nullable=False),
        sa.Column('statdium_name', sa.String(length=40), nullable=False),
        sa.Column('hometeam_id', sa.String(length=10), nullable=True),
        sa.Column('seat_count', sa.Integer(), nullable=True),
        sa.Column('address', sa.String(length=60), nullable=True),
        sa.Column('ddd', sa.String(length=10), nullable=True),
        sa.Column('tel', sa.String(length=10), nullable=True),
        sa.PrimaryKeyConstraint('stadium_id'),
    )

    op.create_table(
        'team',
        sa.Column('team_id', sa.String(length=10), nullable=False),
        sa.Column('region_name', sa.String(length=10), nullable=False),
        sa.Column('team_name', sa.String(length=40), nullable=False),
        sa.Column('e_team_name', sa.String(length=50), nullable=True),
        sa.Column('orig_yyyy', sa.String(length=10), nullable=True),
        sa.Column('zip_code1', sa.String(length=10), nullable=True),
        sa.Column('zip_code2', sa.String(length=10), nullable=True),
        sa.Column('address', sa.String(length=80), nullable=True),
        sa.Column('ddd', sa.String(length=10), nullable=True),
        sa.Column('tel', sa.String(length=10), nullable=True),
        sa.Column('fax', sa.String(length=10), nullable=True),
        sa.Column('homepage', sa.String(length=50), nullable=True),
        sa.Column('owner', sa.String(length=10), nullable=True),
        sa.Column('stadium_id', sa.String(length=10), nullable=True),
        sa.ForeignKeyConstraint(['stadium_id'], ['stadium.stadium_id']),
        sa.PrimaryKeyConstraint('team_id'),
    )

    op.create_table(
        'schedule',
        sa.Column('sche_date', sa.String(length=10), nullable=False),
        sa.Column('stadium_id', sa.String(length=10), nullable=False),
        sa.Column('gubun', sa.String(length=10), nullable=True),
        sa.Column('hometeam_id', sa.String(length=10), nullable=True),
        sa.Column('awayteam_id', sa.String(length=10), nullable=True),
        sa.Column('home_score', sa.Integer(), nullable=True),
        sa.Column('away_score', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['stadium_id'], ['stadium.stadium_id']),
        sa.PrimaryKeyConstraint('sche_date', 'stadium_id'),
    )

    op.create_table(
        'player',
        sa.Column('player_id', sa.String(length=10), nullable=False),
        sa.Column('player_name', sa.String(length=20), nullable=False),
        sa.Column('e_player_name', sa.String(length=40), nullable=True),
        sa.Column('nickname', sa.String(length=30), nullable=True),
        sa.Column('join_yyyy', sa.String(length=10), nullable=True),
        sa.Column('position', sa.String(length=10), nullable=True),
        sa.Column('back_no', sa.Integer(), nullable=True),
        sa.Column('nation', sa.String(length=20), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('solar', sa.String(length=10), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('weight', sa.Integer(), nullable=True),
        sa.Column('team_id', sa.String(length=10), nullable=True),
        sa.Column('player_embedding', Vector(1536), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['team.team_id']),
        sa.PrimaryKeyConstraint('player_id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('player')
    op.drop_table('schedule')
    op.drop_table('team')
    op.drop_table('stadium')
