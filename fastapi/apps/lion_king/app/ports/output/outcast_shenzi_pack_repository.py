from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.app.dtos.outcast_shenzi_pack_dto import ShenziPackQuery, ShenziPackResponse


class ShenziPackRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: ShenziPackQuery) -> ShenziPackResponse:
        '''셴지의 자기 소개 레포지토리 추상 메소드'''
        pass
