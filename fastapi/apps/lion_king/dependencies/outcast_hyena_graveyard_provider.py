from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from lion_king.adapter.outbound.pg.outcast_hyena_graveyard_pg_repository import HyenaGraveyardPgRepository
from lion_king.app.ports.output.outcast_hyena_graveyard_repository import HyenaGraveyardRepository
from core.matrix.grid_oracle_database_manager import get_db
from lion_king.app.ports.input.outcast_hyena_graveyard_use_case import HyenaGraveyardUseCase
from lion_king.app.use_cases.outcast_hyena_graveyard_interactor import HyenaGraveyardInteractor


def get_hyena_graveyard_repository(
        db: AsyncSession = Depends(get_db)
) -> HyenaGraveyardRepository:

    return HyenaGraveyardPgRepository(session=db)


def get_hyena_graveyard_use_case(
        repository: HyenaGraveyardRepository = Depends(get_hyena_graveyard_repository)
) -> HyenaGraveyardUseCase:

    return HyenaGraveyardInteractor(repository=repository)
