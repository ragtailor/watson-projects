from __future__ import annotations

from abc import ABC, abstractmethod


class KerriganIntentPort(ABC):

    @abstractmethod
    def analyze_intent(self, message: str) -> str:
        '''형태소 분석으로 메시지의 의도(카테고리)를 판단하는 추상 메소드 (CPU-bound, 동기)'''
        pass
