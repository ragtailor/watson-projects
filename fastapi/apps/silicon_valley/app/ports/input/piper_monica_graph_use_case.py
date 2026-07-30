from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_monica_graph_dto import MonicaAskQuery, MonicaAskResponse


class PiperMonicaGraphUseCase(ABC):

    @abstractmethod
    async def ask(self, query: MonicaAskQuery) -> MonicaAskResponse:
        '''하이브리드(벡터+그래프) 검색 에이전트로 질문에 답하는 추상 메소드'''
        pass
