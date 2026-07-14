from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_gilfoyle_llm_dto import GilfoyleLlmQuery, GilfoyleLlmResponse


class GilfoyleLlmPort(ABC):

    @abstractmethod
    async def generate(self, query: GilfoyleLlmQuery) -> GilfoyleLlmResponse:
        '''로컬 EXAONE 서버에 생성 요청을 위임하는 추상 메소드'''
        pass
