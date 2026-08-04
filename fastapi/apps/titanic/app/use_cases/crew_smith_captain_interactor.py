from __future__ import annotations

import logging

from pandas import DataFrame
from typing import Dict, Any, List

from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import ChatSchema, SmithCaptainSchema
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery, SmithCaptainResponse, ChatResponse, ReportSummaryResponse
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.ports.output.crew_smith_captain_port import SmithCaptainPort
from titanic.adapter.inbound.api.schemas.passenger_ruth_validation_schema import RuthValidationSchema

logger = logging.getLogger(__name__)

class SmithCaptainInteractor(SmithCaptainUseCase):

    def __init__(
        self,
        repository: SmithCaptainPort,
        andrews: AndrewsArchitectUseCase,
        jack: JackTrainerUseCase,
        rose: RoseModelUseCase,
        cal: CalTesterUseCase,
        walter: WalterRoasterUseCase,
        lowe: LoweBoatUseCase,
        hartley: HartleyViolinUseCase,
    ):
        self.repository = repository
        self.andrews = andrews
        self.jack = jack
        self.rose = rose
        self.cal = cal
        self.walter = walter
        self.lowe = lowe
        self.hartley = hartley

    async def chat(self, schema: ChatSchema) -> ChatResponse:
        import re
        from titanic.domain.value_objects.social_vo import Gender
        from titanic.domain.value_objects.age_vo import Age
        from titanic.domain.value_objects.survived_vo import SurvivalStatus
        from titanic.domain.entities.passenger_jack_trainer_entity import PassengerEntity

        user_messages = [m for m in schema.messages if m.role == "user"]
        question: str = user_messages[-1].text if user_messages else ""

        train_set: DataFrame = self.walter.get_train_set()
        test_set: DataFrame  = self.walter.get_test_set()
        featured_set: List   = self.lowe.feature_engineering(train_set, test_set)

        intent_result = self.andrews.analyze_intent(question)
        intent: str   = intent_result["intent"]
        keywords: list = intent_result["keywords"]

        logger.info(f"[SmithCaptain] chat | intent={intent} keywords={keywords}")

        # ── SURVIVAL_PREDICT ───────────────────────────────────────────
        if intent == "SURVIVAL_PREDICT":
            age_match  = re.search(r"(\d+)\s*세", question)
            age_val    = float(age_match.group(1)) if age_match else None

            text = question + " " + " ".join(keywords)
            if any(k in text for k in ("남자", "남성", "남")):
                gender_str = "male"
            elif any(k in text for k in ("여자", "여성", "여")):
                gender_str = "female"
            else:
                gender_str = "unknown"

            gender = Gender.from_raw(gender_str)
            age    = Age(value=age_val)
            entity = PassengerEntity(
                id=0,
                gender=gender,
                age=age,
                survival_status=SurvivalStatus(survived=None),
            )

            prediction  = await self.jack.predict_survival({"gender": gender_str, "age": age_val})
            survive_prob = prediction.get("probability")
            survived     = prediction.get("survived")

            subject = " ".join(filter(None, [
                f"{int(age_val)}세" if age_val else None,
                {"male": "남성", "female": "여성"}.get(gender_str),
            ])) or "해당 승객"
            risk_note = " (도메인 판단: 통계적 고위험군)" if entity.is_high_risk() else ""

            if survive_prob is not None:
                result = "생존" if survived else "사망"
                return ChatResponse(text=f"{subject} 예측: {result} (생존 확률 {survive_prob:.1%}){risk_note}")
            if entity.is_high_risk():
                return ChatResponse(text=f"{subject}은 고위험군입니다. 통계적으로 생존 가능성이 낮습니다.")
            return ChatResponse(text=f"{subject}은 고위험군에 해당하지 않습니다.")

        # ── STATISTICS ─────────────────────────────────────────────────
        if intent == "STATISTICS":
            features = [
                "survived", "pclass", "age", "sibsp", "parch", "fare",
                "gender", "embarked_code", "family_size", "title",
            ]
            train_df  = featured_set[0]
            available = [f for f in features if f in train_df.columns]
            corr = (
                train_df[available].corr()["survived"]
                .drop("survived")
                .abs()
                .sort_values(ascending=False)
            )
            label = {
                "gender": "성별", "title": "호칭", "pclass": "객실 등급",
                "fare": "운임", "embarked_code": "탑승 항구",
                "age": "나이", "family_size": "가족 수",
                "sibsp": "형제/배우자", "parch": "부모/자녀",
            }
            lines = ["📊 생존율과의 상관관계 순위\n"]
            for rank, (feat, val) in enumerate(corr.items(), 1):
                bar = "█" * int(val * 10)
                lines.append(f"{rank}. {label.get(feat, feat)}: {val:.2f} {bar}")
            lines.append("\n가장 중요한 피처는 '성별'입니다. 여성의 생존율이 압도적으로 높았습니다.")
            return ChatResponse(text="\n".join(lines))

        # ── MODEL_TRAIN ────────────────────────────────────────────────
        if intent == "MODEL_TRAIN":
            result = await self.jack.train_model(featured_set[0])
            accuracy = result.get("accuracy")
            if accuracy:
                return ChatResponse(text=f"모델 학습 완료. 정확도: {accuracy:.1%}")
            return ChatResponse(text="모델 학습이 완료되었습니다.")

        # ── PASSENGER_SEARCH ───────────────────────────────────────────
        if intent == "PASSENGER_SEARCH":
            train_df = featured_set[0]
            lines = ["📋 승객 통계\n"]
            if "gender" in train_df.columns:
                male_rate   = train_df[train_df["gender"] == 0]["survived"].mean()
                female_rate = train_df[train_df["gender"] == 1]["survived"].mean()
                lines.append(f"남성 생존율: {male_rate:.1%}")
                lines.append(f"여성 생존율: {female_rate:.1%}")
            if "pclass" in train_df.columns:
                for cls in [1, 2, 3]:
                    rate = train_df[train_df["pclass"] == cls]["survived"].mean()
                    lines.append(f"{cls}등급 생존율: {rate:.1%}")
            return ChatResponse(text="\n".join(lines))

        # ── UNKNOWN ────────────────────────────────────────────────────
        return ChatResponse(text=(
            "질문의 의도를 파악하지 못했습니다.\n"
            "예: '33세 남자라면 살 수 있었을까?', '생존율에 중요한 것이 뭐야?'"
        ))
       
    def get_report_summary(self) -> ReportSummaryResponse:
        from datetime import datetime, timezone

        train_df = self.walter.get_train_set()
        test_df = self.walter.get_test_set()
        featured_set = self.lowe.feature_engineering(train_df, test_df)
        df = featured_set[0]

        if df.empty:
            return ReportSummaryResponse(
                generated_at=datetime.now(timezone.utc).isoformat(),
                total_passengers=0, total_survivors=0, survival_rate=0.0,
                male_survival_rate=0.0, female_survival_rate=0.0,
                class_1_survival_rate=0.0, class_2_survival_rate=0.0, class_3_survival_rate=0.0,
                avg_age=0.0,
            )

        def class_rate(cls: int) -> float:
            subset = df[df["pclass"] == cls] if "pclass" in df.columns else df.iloc[0:0]
            return round(float(subset["survived"].mean()), 4) if not subset.empty else 0.0

        return ReportSummaryResponse(
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_passengers=len(df),
            total_survivors=int(df["survived"].sum()),
            survival_rate=round(float(df["survived"].mean()), 4),
            male_survival_rate=round(float(df[df["gender"] == 0]["survived"].mean()), 4) if "gender" in df.columns else 0.0,
            female_survival_rate=round(float(df[df["gender"] == 1]["survived"].mean()), 4) if "gender" in df.columns else 0.0,
            class_1_survival_rate=class_rate(1),
            class_2_survival_rate=class_rate(2),
            class_3_survival_rate=class_rate(3),
            avg_age=round(float(df["age"].mean()), 1) if "age" in df.columns else 0.0,
        )

    async def introduce_myself(self, schema: SmithCaptainSchema) -> SmithCaptainResponse:
        '''스미스 선장의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(SmithCaptainQuery(
            id = schema.id,
            name = schema.name
        ))

 