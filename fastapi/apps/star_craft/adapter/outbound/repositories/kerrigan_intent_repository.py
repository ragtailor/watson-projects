from __future__ import annotations

import logging

from kiwipiepy import Kiwi

from star_craft.app.ports.output.kerrigan_intent_port import KerriganIntentPort
from star_craft.domain.kerrigan_intent_map import INTENT_MAP

logger = logging.getLogger(__name__)


class KerriganIntentRepository(KerriganIntentPort):
    """Kiwi 형태소 분석 기반 키워드 스코어링으로 의도를 판단한다 (titanic intent_map과 동일한 방식)."""

    def __init__(self) -> None:
        self.kiwi = Kiwi()

    def analyze_intent(self, message: str) -> str:
        tokens = self.kiwi.tokenize(message)
        keywords = [t.form for t in tokens if t.tag.startswith(("NN", "VV", "VA", "XR"))]

        scores: dict[str, int] = {intent: 0 for intent in INTENT_MAP}
        for keyword in keywords:
            for intent, kw_set in INTENT_MAP.items():
                if keyword in kw_set:
                    scores[intent] += 1

        best_intent = max(scores, key=lambda k: scores[k])
        intent = best_intent if scores[best_intent] > 0 else "UNKNOWN"

        logger.info(
            f"[KerriganIntentRepository] analyze_intent | message={message!r} "
            f"intent={intent} scores={scores}"
        )
        return intent
