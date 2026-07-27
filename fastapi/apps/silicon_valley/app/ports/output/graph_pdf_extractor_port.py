from __future__ import annotations

from abc import ABC, abstractmethod


class GraphPdfExtractorPort(ABC):

    @abstractmethod
    async def extract_text(self, filename: str, file_bytes: bytes) -> str:
        '''PDF 바이너리에서 본문 텍스트를 추출하는 추상 메소드'''
        pass
