from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from lion_king.adapter.outbound.pg.pride_mufasa_news_pg_repository import MufasaNewsPgRepository
from lion_king.app.ports.output.pride_mufasa_news_repository import MufasaNewsRepository
from core.matrix.grid_oracle_database_manager import get_db
from lion_king.app.ports.input.pride_mufasa_news_use_case import MufasaNewsUseCase
from lion_king.app.use_cases.pride_mufasa_news_interactor import MufasaNewsInteractor


def get_mufasa_news_repository(
        db: AsyncSession = Depends(get_db)
) -> MufasaNewsRepository:

    return MufasaNewsPgRepository(session=db)


def get_mufasa_news_use_case(
        repository: MufasaNewsRepository = Depends(get_mufasa_news_repository)
) -> MufasaNewsUseCase:

    return MufasaNewsInteractor(repository=repository)
