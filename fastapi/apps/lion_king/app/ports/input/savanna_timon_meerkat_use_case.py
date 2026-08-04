from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.adapter.inbound.api.schemas.savanna_timon_meerkat_schema import TimonMeerkatSchema
from lion_king.app.dtos.savanna_timon_meerkat_dto import TimonMeerkatResponse


class TimonMeerkatUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: TimonMeerkatSchema) -> TimonMeerkatResponse:
        '''티몬의 자기소개 메소드'''
        pass
