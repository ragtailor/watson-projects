from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.domain.document_vector import DocumentVector


class DocumentReaderPort(ABC):
    '''문서 단건 조회. morningstar의 최신 목록 조회(MorningstarReportRepositoryPort)와
    쓰임이 달라 별도 포트로 둔다.'''

    @abstractmethod
    async def find_by_id(self, document_id: int) -> DocumentVector | None:
        '''문서를 id로 조회하는 추상 메소드. 없으면 None을 반환한다.'''
        pass
