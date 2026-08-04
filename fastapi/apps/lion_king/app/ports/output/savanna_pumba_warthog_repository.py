from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.app.dtos.savanna_pumba_warthog_dto import PumbaWarthogQuery, PumbaWarthogResponse


class PumbaWarthogRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: PumbaWarthogQuery) -> PumbaWarthogResponse:
        '''품바의 자기 소개 레포지토리 추상 메소드'''
        pass
