from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from lion_king.adapter.outbound.pg.pride_sarabi_guardian_pg_repository import SarabiGuardianPgRepository
from lion_king.app.ports.output.pride_sarabi_guardian_repository import SarabiGuardianRepository
from core.matrix.grid_oracle_database_manager import get_db
from lion_king.app.ports.input.pride_sarabi_guardian_use_case import SarabiGuardianUseCase
from lion_king.app.use_cases.pride_sarabi_guardian_interactor import SarabiGuardianInteractor


def get_sarabi_guardian_repository(
        db: AsyncSession = Depends(get_db)
) -> SarabiGuardianRepository:

    return SarabiGuardianPgRepository(session=db)


def get_sarabi_guardian_use_case(
        repository: SarabiGuardianRepository = Depends(get_sarabi_guardian_repository)
) -> SarabiGuardianUseCase:

    return SarabiGuardianInteractor(repository=repository)
