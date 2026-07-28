from fastapi import APIRouter, Depends

from silicon_valley.adapter.inbound.api.schemas.morningstar_insight_schema import (
    MorningstarInsightResultSchema,
    MorningstarInsightSchema,
)
from silicon_valley.app.dtos.morningstar_insight_dto import MorningstarInsightCommand
from silicon_valley.app.ports.input.morningstar_insight_use_case import MorningstarInsightUseCase
from silicon_valley.dependencies.morningstar_insight_provider import get_morningstar_insight_use_case

'''
Morningstar 전략: LangChain으로 최신 재무 보고서(실시간 데이터)와 맞춤형 프롬프팅을 결합해
금융 전문가에게 개인화된 인사이트를 제공하는 인텔리전스 엔진.
'''
morningstar_insight_router = APIRouter(prefix="/morningstar", tags=["morningstar"])


@morningstar_insight_router.post(
    "/insight",
    response_model=MorningstarInsightResultSchema,
    summary="최신 재무 보고서 기반 맞춤형 금융 인사이트 생성",
)
async def ask_insight(
    schema: MorningstarInsightSchema,
    use_case: MorningstarInsightUseCase = Depends(get_morningstar_insight_use_case),
) -> MorningstarInsightResultSchema:

    response = await use_case.ask(
        MorningstarInsightCommand(question=schema.question, report_limit=schema.report_limit)
    )

    return MorningstarInsightResultSchema(
        question=response.question,
        insight=response.insight,
        sources=response.sources,
    )
