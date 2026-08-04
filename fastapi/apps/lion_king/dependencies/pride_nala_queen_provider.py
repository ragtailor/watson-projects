from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from lion_king.adapter.outbound.pg.pride_nala_queen_pg_repository import NalaQueenPgRepository
from lion_king.app.ports.output.pride_nala_queen_repository import NalaQueenRepository
from core.matrix.grid_oracle_database_manager import get_db
from lion_king.app.ports.input.pride_nala_queen_use_case import NalaQueenUseCase
from lion_king.app.use_cases.pride_nala_queen_interactor import NalaQueenInteractor


def get_nala_queen_repository(
        db: AsyncSession = Depends(get_db)
) -> NalaQueenRepository:

    return NalaQueenPgRepository(session=db)


def get_nala_queen_use_case(
        repository: NalaQueenRepository = Depends(get_nala_queen_repository)
) -> NalaQueenUseCase:

    return NalaQueenInteractor(repository=repository)
