from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from lion_king.adapter.outbound.pg.savanna_pumba_warthog_pg_repository import PumbaWarthogPgRepository
from lion_king.app.ports.output.savanna_pumba_warthog_repository import PumbaWarthogRepository
from core.matrix.grid_oracle_database_manager import get_db
from lion_king.app.ports.input.savanna_pumba_warthog_use_case import PumbaWarthogUseCase
from lion_king.app.use_cases.savanna_pumba_warthog_interactor import PumbaWarthogInteractor


def get_pumba_warthog_repository(
        db: AsyncSession = Depends(get_db)
) -> PumbaWarthogRepository:

    return PumbaWarthogPgRepository(session=db)


def get_pumba_warthog_use_case(
        repository: PumbaWarthogRepository = Depends(get_pumba_warthog_repository)
) -> PumbaWarthogUseCase:

    return PumbaWarthogInteractor(repository=repository)
