from __future__ import annotations
from abc import ABC, abstractmethod
from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import SmithCaptainSchema, ChatSchema
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainResponse, ChatResponse, ReportSummaryResponse
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase

class SmithCaptainUseCase(ABC):

    @abstractmethod
    def introduce_myself(self, schema: SmithCaptainSchema) -> SmithCaptainResponse:
        '''스미스 선장의 자기소개 메소드'''
        pass

    @abstractmethod
    async def chat(self, schema: ChatSchema) -> ChatResponse:
        '''사용자 자연어 입력을 받아 채팅 응답을 반환'''
        pass

    @abstractmethod
    def get_report_summary(self) -> ReportSummaryResponse:
        '''승객 통계를 집계하여 보고서 데이터를 반환'''
        pass