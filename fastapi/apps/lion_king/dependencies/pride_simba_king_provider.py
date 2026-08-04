from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from lion_king.adapter.outbound.pg.pride_simba_king_pg_repository import SimbaKingPgRepository
from lion_king.app.ports.output.pride_simba_king_repository import SimbaKingRepository
from core.matrix.grid_oracle_database_manager import get_db
from lion_king.app.ports.input.pride_simba_king_use_case import SimbaKingUseCase
from lion_king.app.use_cases.pride_simba_king_interactor import SimbaKingInteractor


def get_simba_king_repository(
        db: AsyncSession = Depends(get_db)
) -> SimbaKingRepository:

    return SimbaKingPgRepository(session=db)


def get_simba_king_use_case(
        repository: SimbaKingRepository = Depends(get_simba_king_repository)
) -> SimbaKingUseCase:

    return SimbaKingInteractor(repository=repository)
