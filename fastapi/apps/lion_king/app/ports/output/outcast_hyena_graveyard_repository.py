from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.app.dtos.outcast_hyena_graveyard_dto import HyenaGraveyardQuery, HyenaGraveyardResponse


class HyenaGraveyardRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: HyenaGraveyardQuery) -> HyenaGraveyardResponse:
        '''하이에나 무리의 자기 소개 레포지토리 추상 메소드'''
        pass
