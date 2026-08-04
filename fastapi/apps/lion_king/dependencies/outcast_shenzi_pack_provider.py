from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from lion_king.adapter.outbound.pg.outcast_shenzi_pack_pg_repository import ShenziPackPgRepository
from lion_king.app.ports.output.outcast_shenzi_pack_repository import ShenziPackRepository
from core.matrix.grid_oracle_database_manager import get_db
from lion_king.app.ports.input.outcast_shenzi_pack_use_case import ShenziPackUseCase
from lion_king.app.use_cases.outcast_shenzi_pack_interactor import ShenziPackInteractor


def get_shenzi_pack_repository(
        db: AsyncSession = Depends(get_db)
) -> ShenziPackRepository:

    return ShenziPackPgRepository(session=db)


def get_shenzi_pack_use_case(
        repository: ShenziPackRepository = Depends(get_shenzi_pack_repository)
) -> ShenziPackUseCase:

    return ShenziPackInteractor(repository=repository)
