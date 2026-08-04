from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.app.dtos.pride_mufasa_news_dto import MufasaNewsQuery, MufasaNewsResponse


class MufasaNewsRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: MufasaNewsQuery) -> MufasaNewsResponse:
        '''무파사의 자기 소개 레포지토리 추상 메소드'''
        pass
