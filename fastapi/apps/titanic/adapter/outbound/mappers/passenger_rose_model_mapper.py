from __future__ import annotations

from typing import Any

# 이 매퍼가 다루는 값(pclass/ticket/fare/cabin/embarked)은 bookings 테이블에 있다.
# 전용 passenger_rose_model_orm은 존재한 적이 없어, 실제 소유 ORM인 SmithCaptainOrm을 쓴다.
from titanic.adapter.outbound.orm.crew_smith_captain_orm import SmithCaptainOrm as RoseModelOrm

# RoseModelEntity is not yet defined — mapper provides ORM ↔ dict conversion
# until the domain entity is implemented.


class RoseModelMapper:

    @staticmethod
    def to_dict(orm: RoseModelOrm) -> dict[str, Any]:
        return {
            "id": orm.id,
            "passenger_id": orm.passenger_id,
            "pclass": orm.pclass,
            "ticket": orm.ticket,
            "fare": orm.fare,
            "cabin": orm.cabin,
            "embarked": orm.embarked,
        }

    @staticmethod
    def to_orm(
        passenger_id: str | None,
        pclass: str | None,
        ticket: str | None,
        fare: str | None,
        cabin: str | None,
        embarked: str | None,
    ) -> RoseModelOrm:
        return RoseModelOrm(
            passenger_id=passenger_id,
            pclass=pclass,
            ticket=ticket,
            fare=fare,
            cabin=cabin,
            embarked=embarked,
        )
