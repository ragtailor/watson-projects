from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.morningstar_insight_dto import MorningstarInsightCommand, MorningstarInsightResponse


class MorningstarInsightUseCase(ABC):

    @abstractmethod
    async def ask(self, command: MorningstarInsightCommand) -> MorningstarInsightResponse:
        '''질문에 대해 최신 재무 보고서를 근거로 맞춤형 금융 인사이트를 생성하는 메소드'''
        pass
