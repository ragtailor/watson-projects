from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.app.dtos.pride_simba_king_dto import SimbaKingQuery, SimbaKingResponse


class SimbaKingRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: SimbaKingQuery) -> SimbaKingResponse:
        '''심바의 자기 소개 레포지토리 추상 메소드'''
        pass
