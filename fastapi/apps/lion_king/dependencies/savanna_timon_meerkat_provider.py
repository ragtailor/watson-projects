from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from lion_king.adapter.outbound.pg.savanna_timon_meerkat_pg_repository import TimonMeerkatPgRepository
from lion_king.app.ports.output.savanna_timon_meerkat_repository import TimonMeerkatRepository
from core.matrix.grid_oracle_database_manager import get_db
from lion_king.app.ports.input.savanna_timon_meerkat_use_case import TimonMeerkatUseCase
from lion_king.app.use_cases.savanna_timon_meerkat_interactor import TimonMeerkatInteractor


def get_timon_meerkat_repository(
        db: AsyncSession = Depends(get_db)
) -> TimonMeerkatRepository:

    return TimonMeerkatPgRepository(session=db)


def get_timon_meerkat_use_case(
        repository: TimonMeerkatRepository = Depends(get_timon_meerkat_repository)
) -> TimonMeerkatUseCase:

    return TimonMeerkatInteractor(repository=repository)
