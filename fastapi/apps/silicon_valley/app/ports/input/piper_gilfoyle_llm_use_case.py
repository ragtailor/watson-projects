from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.adapter.inbound.api.schemas.piper_gilfoyle_llm_schema import GilfoyleLlmSchema
from silicon_valley.app.dtos.piper_gilfoyle_llm_dto import GilfoyleLlmResponse


class GilfoyleLlmUseCase(ABC):

    @abstractmethod
    async def generate(self, schema: GilfoyleLlmSchema) -> GilfoyleLlmResponse:
        '''길포일이 로컬 LLM으로 텍스트를 생성하는 메소드'''
        pass
