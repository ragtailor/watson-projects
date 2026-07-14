from fastapi import APIRouter, Depends

from silicon_valley.adapter.inbound.api.schemas.piper_gilfoyle_llm_schema import GilfoyleLlmSchema
from silicon_valley.app.dtos.piper_gilfoyle_llm_dto import GilfoyleLlmResponse
from silicon_valley.app.ports.input.piper_gilfoyle_llm_use_case import GilfoyleLlmUseCase
from silicon_valley.dependencies.piper_gilfoyle_llm_provider import get_gilfoyle_llm_use_case

'''
버트람 길포일 (Bertram Gilfoyle)
피드 파이퍼의 시스템 아키텍트. 로컬에 띄운 EXAONE 모델로 텍스트를 생성한다.
'''
gilfoyle_llm_router = APIRouter(prefix="/gilfoyle", tags=["gilfoyle"])


@gilfoyle_llm_router.post("/llm/generate")
async def generate(
    schema: GilfoyleLlmSchema,
    gilfoyle: GilfoyleLlmUseCase = Depends(get_gilfoyle_llm_use_case),
) -> GilfoyleLlmResponse:

    return await gilfoyle.generate(schema)
