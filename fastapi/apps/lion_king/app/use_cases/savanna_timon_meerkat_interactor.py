from __future__ import annotations

from lion_king.adapter.inbound.api.schemas.savanna_timon_meerkat_schema import TimonMeerkatSchema
from lion_king.app.dtos.savanna_timon_meerkat_dto import TimonMeerkatQuery, TimonMeerkatResponse
from lion_king.app.ports.input.savanna_timon_meerkat_use_case import TimonMeerkatUseCase
from lion_king.app.ports.output.savanna_timon_meerkat_repository import TimonMeerkatRepository


class TimonMeerkatInteractor(TimonMeerkatUseCase):

    def __init__(self, repository: TimonMeerkatRepository):
        self.repository = repository

    async def introduce_myself(self, schema: TimonMeerkatSchema) -> TimonMeerkatResponse:
        '''티몬의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(TimonMeerkatQuery(
            id = schema.id,
            name = schema.name
        ))
