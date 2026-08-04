from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.app.dtos.shaman_rafiki_faq_dto import RafikiFaqQuery, RafikiFaqResponse


class RafikiFaqRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: RafikiFaqQuery) -> RafikiFaqResponse:
        '''라피키의 자기 소개 레포지토리 추상 메소드'''
        pass
