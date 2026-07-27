from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.domain.document_vector import DocumentVector


class MorningstarReportRepositoryPort(ABC):

    @abstractmethod
    async def find_recent_reports(self, limit: int) -> list[DocumentVector]:
        '''최근 저장된 재무 보고서를 실시간으로 조회하는 추상 메소드'''
        pass
