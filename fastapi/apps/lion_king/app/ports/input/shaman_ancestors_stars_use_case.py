from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.adapter.inbound.api.schemas.shaman_ancestors_stars_schema import AncestorsStarsSchema
from lion_king.app.dtos.shaman_ancestors_stars_dto import AncestorsStarsResponse


class AncestorsStarsUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: AncestorsStarsSchema) -> AncestorsStarsResponse:
        '''선조들의 자기소개 메소드'''
        pass
