from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from lion_king.adapter.outbound.pg.shaman_ancestors_stars_pg_repository import AncestorsStarsPgRepository
from lion_king.app.ports.output.shaman_ancestors_stars_repository import AncestorsStarsRepository
from core.matrix.grid_oracle_database_manager import get_db
from lion_king.app.ports.input.shaman_ancestors_stars_use_case import AncestorsStarsUseCase
from lion_king.app.use_cases.shaman_ancestors_stars_interactor import AncestorsStarsInteractor


def get_ancestors_stars_repository(
        db: AsyncSession = Depends(get_db)
) -> AncestorsStarsRepository:

    return AncestorsStarsPgRepository(session=db)


def get_ancestors_stars_use_case(
        repository: AncestorsStarsRepository = Depends(get_ancestors_stars_repository)
) -> AncestorsStarsUseCase:

    return AncestorsStarsInteractor(repository=repository)
