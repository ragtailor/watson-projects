from __future__ import annotations

from abc import ABC, abstractmethod


class GraphReasoningPort(ABC):

    @abstractmethod
    async def find_related(self, keywords: list[str], limit: int) -> list[str]:
        '''키워드와 연결된 관계망을 사람이 읽을 수 있는 문장 목록으로 반환하는 추상 메소드'''
        pass
