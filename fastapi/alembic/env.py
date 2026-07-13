import os
import sys
import types
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# backend/apps/ 를 sys.path에 추가해야 titanic.* 임포트가 가능
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps"))

# 디렉터리가 tailor/ → fastapi/ 로 변경되면서 'tailor' 패키지를 못 찾는 문제 해결.
# main.py와 동일하게 sys.modules에 alias를 등록해 from tailor.xxx import ... 가 fastapi/ 를 가리키게 한다.
_tailor_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_tailor_alias = types.ModuleType("tailor")
_tailor_alias.__path__ = [_tailor_root]
_tailor_alias.__package__ = "tailor"
sys.modules.setdefault("tailor", _tailor_alias)

from core.config import DATABASE_URL
from tailor.core.matrix.grid_oracle_database_manager import Base

# autogenerate가 두 테이블을 인식하도록 ORM 모델을 반드시 임포트
import titanic.adapter.outbound.orm.passenger_jack_trainer_orm  # noqa: F401
import titanic.adapter.outbound.orm.crew_smith_captain_orm  # noqa: F401
import moneyball.adapter.outbound.orm.stadium_orm  # noqa: F401
import moneyball.adapter.outbound.orm.team_orm  # noqa: F401
import moneyball.adapter.outbound.orm.schedule_orm  # noqa: F401
import moneyball.adapter.outbound.orm.player_orm  # noqa: F401

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
