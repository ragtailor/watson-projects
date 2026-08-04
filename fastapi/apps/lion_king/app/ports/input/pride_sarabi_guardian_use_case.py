from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.adapter.inbound.api.schemas.pride_sarabi_guardian_schema import SarabiGuardianSchema
from lion_king.app.dtos.pride_sarabi_guardian_dto import SarabiGuardianResponse


class SarabiGuardianUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: SarabiGuardianSchema) -> SarabiGuardianResponse:
        '''사라비의 자기소개 메소드'''
        pass
