from __future__ import annotations

from silicon_valley.adapter.inbound.api.schemas.piper_gilfoyle_llm_schema import GilfoyleLlmSchema
from silicon_valley.app.dtos.piper_gilfoyle_llm_dto import GilfoyleLlmQuery, GilfoyleLlmResponse
from silicon_valley.app.ports.input.piper_gilfoyle_llm_use_case import GilfoyleLlmUseCase
from silicon_valley.app.ports.output.piper_gilfoyle_llm_port import GilfoyleLlmPort


class GilfoyleLlmInteractor(GilfoyleLlmUseCase):

    def __init__(self, client: GilfoyleLlmPort):
        self.client = client

    async def generate(self, schema: GilfoyleLlmSchema) -> GilfoyleLlmResponse:
        '''길포일 LLM 생성 인터랙트'''

        return await self.client.generate(GilfoyleLlmQuery(
            prompt=schema.prompt,
            max_new_tokens=schema.max_new_tokens,
            temperature=schema.temperature,
        ))
