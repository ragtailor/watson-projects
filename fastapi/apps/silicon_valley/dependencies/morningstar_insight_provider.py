from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from silicon_valley.adapter.outbound.client.morningstar_insight_generator_client import (
    MorningstarInsightGeneratorClient,
)
from silicon_valley.adapter.outbound.repository.morningstar_report_repository import MorningstarReportRepository
from silicon_valley.app.ports.input.morningstar_insight_use_case import MorningstarInsightUseCase
from silicon_valley.app.ports.output.morningstar_insight_generator_port import MorningstarInsightGeneratorPort
from silicon_valley.app.ports.output.morningstar_report_repository_port import MorningstarReportRepositoryPort
from silicon_valley.app.use_cases.morningstar_insight_interactor import MorningstarInsightInteractor


def get_morningstar_report_repository(
    db: AsyncSession = Depends(get_db),
) -> MorningstarReportRepositoryPort:
    return MorningstarReportRepository(session=db)


def get_morningstar_insight_generator() -> MorningstarInsightGeneratorPort:
    return MorningstarInsightGeneratorClient()


def get_morningstar_insight_use_case(
    report_repository: MorningstarReportRepositoryPort = Depends(get_morningstar_report_repository),
    generator: MorningstarInsightGeneratorPort = Depends(get_morningstar_insight_generator),
) -> MorningstarInsightUseCase:

    return MorningstarInsightInteractor(report_repository=report_repository, generator=generator)
