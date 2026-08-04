from __future__ import annotations

from lion_king.adapter.inbound.api.schemas.shaman_ancestors_stars_schema import AncestorsStarsSchema
from lion_king.app.dtos.shaman_ancestors_stars_dto import AncestorsStarsQuery, AncestorsStarsResponse
from lion_king.app.ports.input.shaman_ancestors_stars_use_case import AncestorsStarsUseCase
from lion_king.app.ports.output.shaman_ancestors_stars_repository import AncestorsStarsRepository


class AncestorsStarsInteractor(AncestorsStarsUseCase):

    def __init__(self, repository: AncestorsStarsRepository):
        self.repository = repository

    async def introduce_myself(self, schema: AncestorsStarsSchema) -> AncestorsStarsResponse:
        '''선조들의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(AncestorsStarsQuery(
            id = schema.id,
            name = schema.name
        ))
