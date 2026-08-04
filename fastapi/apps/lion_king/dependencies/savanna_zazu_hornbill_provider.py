from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from lion_king.adapter.outbound.pg.savanna_zazu_hornbill_pg_repository import ZazuHornbillPgRepository
from lion_king.app.ports.output.savanna_zazu_hornbill_repository import ZazuHornbillRepository
from core.matrix.grid_oracle_database_manager import get_db
from lion_king.app.ports.input.savanna_zazu_hornbill_use_case import ZazuHornbillUseCase
from lion_king.app.use_cases.savanna_zazu_hornbill_interactor import ZazuHornbillInteractor


def get_zazu_hornbill_repository(
        db: AsyncSession = Depends(get_db)
) -> ZazuHornbillRepository:

    return ZazuHornbillPgRepository(session=db)


def get_zazu_hornbill_use_case(
        repository: ZazuHornbillRepository = Depends(get_zazu_hornbill_repository)
) -> ZazuHornbillUseCase:

    return ZazuHornbillInteractor(repository=repository)
