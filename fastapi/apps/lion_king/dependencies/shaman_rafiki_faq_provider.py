from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from lion_king.adapter.outbound.pg.shaman_rafiki_faq_pg_repository import RafikiFaqPgRepository
from lion_king.app.ports.output.shaman_rafiki_faq_repository import RafikiFaqRepository
from core.matrix.grid_oracle_database_manager import get_db
from lion_king.app.ports.input.shaman_rafiki_faq_use_case import RafikiFaqUseCase
from lion_king.app.use_cases.shaman_rafiki_faq_interactor import RafikiFaqInteractor


def get_rafiki_faq_repository(
        db: AsyncSession = Depends(get_db)
) -> RafikiFaqRepository:

    return RafikiFaqPgRepository(session=db)


def get_rafiki_faq_use_case(
        repository: RafikiFaqRepository = Depends(get_rafiki_faq_repository)
) -> RafikiFaqUseCase:

    return RafikiFaqInteractor(repository=repository)
