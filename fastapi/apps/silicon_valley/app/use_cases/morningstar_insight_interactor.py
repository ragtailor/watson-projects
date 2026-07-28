from __future__ import annotations

from silicon_valley.app.dtos.morningstar_insight_dto import MorningstarInsightCommand, MorningstarInsightResponse
from silicon_valley.app.ports.input.morningstar_insight_use_case import MorningstarInsightUseCase
from silicon_valley.app.ports.output.morningstar_insight_generator_port import MorningstarInsightGeneratorPort
from silicon_valley.app.ports.output.morningstar_report_repository_port import MorningstarReportRepositoryPort


class MorningstarInsightInteractor(MorningstarInsightUseCase):

    def __init__(
        self,
        report_repository: MorningstarReportRepositoryPort,
        generator: MorningstarInsightGeneratorPort,
    ):
        self.report_repository = report_repository
        self.generator = generator

    async def ask(self, command: MorningstarInsightCommand) -> MorningstarInsightResponse:
        '''최신 보고서 조회(실시간 데이터 통합) → LangChain 맞춤형 프롬프팅으로 인사이트 생성'''

        reports = await self.report_repository.find_recent_reports(command.report_limit)
        insight = await self.generator.generate(command.question, reports)

        return MorningstarInsightResponse(
            question=command.question,
            insight=insight,
            sources=[report.filename for report in reports],
        )
