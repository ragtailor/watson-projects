from __future__ import annotations

from abc import ABC, abstractmethod

from lion_king.app.dtos.pride_sarabi_guardian_dto import SarabiGuardianQuery, SarabiGuardianResponse


class SarabiGuardianRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: SarabiGuardianQuery) -> SarabiGuardianResponse:
        '''사라비의 자기 소개 레포지토리 추상 메소드'''
        pass
