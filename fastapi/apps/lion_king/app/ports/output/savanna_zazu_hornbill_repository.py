from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.app.dtos.savanna_zazu_hornbill_dto import ZazuHornbillQuery, ZazuHornbillResponse


class ZazuHornbillRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: ZazuHornbillQuery) -> ZazuHornbillResponse:
        '''자주의 자기 소개 레포지토리 추상 메소드'''
        pass
