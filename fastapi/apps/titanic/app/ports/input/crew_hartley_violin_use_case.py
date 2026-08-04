from __future__ import annotations

from abc import ABC, abstractmethod

from pandas import DataFrame

from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schema import HartleyViolinSchema
from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinResponse


class HartleyViolinUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: HartleyViolinSchema) -> HartleyViolinResponse:
        '''하틀리 바이올린의 자기소개 메소드'''
        pass

    @abstractmethod
    def get_correlation_chart(self, df: DataFrame) -> bytes:
        '''수치형 피처 상관관계 히트맵을 PNG bytes로 반환'''
        pass
