from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.app.dtos.savanna_timon_meerkat_dto import TimonMeerkatQuery, TimonMeerkatResponse


class TimonMeerkatRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: TimonMeerkatQuery) -> TimonMeerkatResponse:
        '''티몬의 자기 소개 레포지토리 추상 메소드'''
        pass
