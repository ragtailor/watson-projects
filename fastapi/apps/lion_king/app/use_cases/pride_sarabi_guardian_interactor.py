from __future__ import annotations

from lion_king.adapter.inbound.api.schemas.pride_sarabi_guardian_schema import SarabiGuardianSchema
from lion_king.app.dtos.pride_sarabi_guardian_dto import SarabiGuardianQuery, SarabiGuardianResponse
from lion_king.app.ports.input.pride_sarabi_guardian_use_case import SarabiGuardianUseCase
from lion_king.app.ports.output.pride_sarabi_guardian_repository import SarabiGuardianRepository


class SarabiGuardianInteractor(SarabiGuardianUseCase):

    def __init__(self, repository: SarabiGuardianRepository):
        self.repository = repository

    async def introduce_myself(self, schema: SarabiGuardianSchema) -> SarabiGuardianResponse:
        '''사라비의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(SarabiGuardianQuery(
            id = schema.id,
            name = schema.name
        ))
