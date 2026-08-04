from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.app.dtos.shaman_ancestors_stars_dto import AncestorsStarsQuery, AncestorsStarsResponse


class AncestorsStarsRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: AncestorsStarsQuery) -> AncestorsStarsResponse:
        '''선조들의 자기 소개 레포지토리 추상 메소드'''
        pass
