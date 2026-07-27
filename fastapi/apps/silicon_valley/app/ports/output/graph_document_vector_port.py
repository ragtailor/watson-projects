from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.domain.document_vector import DocumentVector


class GraphDocumentVectorPort(ABC):

    @abstractmethod
    async def save(self, filename: str, content: str, summary: str) -> DocumentVector:
        '''추출·요약된 문서를 영속화하는 추상 메소드'''
        pass
