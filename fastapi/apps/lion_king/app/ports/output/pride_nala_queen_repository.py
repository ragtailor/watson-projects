from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.app.dtos.pride_nala_queen_dto import NalaQueenQuery, NalaQueenResponse


class NalaQueenRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: NalaQueenQuery) -> NalaQueenResponse:
        '''날라의 자기 소개 레포지토리 추상 메소드'''
        pass
