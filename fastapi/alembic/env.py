import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# main.py와 같은 임포트 경로를 만든다: fastapi/ → core.*, fastapi/apps/ → titanic 등 앱
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _root)
sys.path.insert(0, os.path.join(_root, "apps"))

from core.config import DATABASE_URL
from core.matrix.grid_oracle_database_manager import Base

# autogenerate가 두 테이블을 인식하도록 ORM 모델을 반드시 임포트
import titanic.adapter.outbound.orm.passenger_jack_trainer_orm  # noqa: F401
import titanic.adapter.outbound.orm.crew_smith_captain_orm  # noqa: F401
import moneyball.adapter.outbound.orm.stadium_orm  # noqa: F401
import moneyball.adapter.outbound.orm.team_orm  # noqa: F401
import moneyball.adapter.outbound.orm.schedule_orm  # noqa: F401
import moneyball.adapter.outbound.orm.player_orm  # noqa: F401
import silicon_valley.adapter.outbound.orm.document_vector_orm  # noqa: F401
import silicon_valley.adapter.outbound.orm.knowledge_chunk_orm  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
