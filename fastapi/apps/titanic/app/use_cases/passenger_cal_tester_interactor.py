from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTesterSchema
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterQuery, CalTesterResponse
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.output.passenger_cal_tester_port import CalTesterPort
from titanic.app.ports.output.passenger_rose_model_port import RoseModelPort

logger = logging.getLogger(__name__)


class CalTesterInteractor(CalTesterUseCase):

    def __init__(self, repository: CalTesterPort):
        self.repository = repository

    async def test_model(self, test_set: dict[str, Any]) -> dict[str, Any]:
        '''칼이 로즈가 제안한 10개 모델의 트레이닝 정도를 점수화 해서 1등을 뽑는것

        Args:
            test_set: {
                "df":                pd.DataFrame,              # 원본 테스트 데이터 (Survived 컬럼 포함)
                "trained_strategies": dict[str, SurvivalModelStrategy],  # Jack이 학습시킨 모델들
            }
        '''
        logger.info("[CalTesterInteractor] 모델 채점 시작")

        trained_strategies: dict[str, RoseModelPort] = test_set["trained_strategies"]
        X_test, y_test = _preprocess_test(test_set["df"])

        results: list[dict[str, Any]] = []
        for key, strategy in trained_strategies.items():
            try:
                predictions = strategy.predict(X_test)
                correct = sum(p == t for p, t in zip(predictions, y_test))
                accuracy = correct / len(y_test)
                results.append({
                    "key": key,
                    "name": strategy.name,
                    "accuracy": round(accuracy, 4),
                    "correct": correct,
                    "total": len(y_test),
                })
                logger.info(f"[CalTesterInteractor] {strategy.name} | accuracy={accuracy:.4f}")
            except Exception as e:
                results.append({
                    "key": key,
                    "name": key,
                    "accuracy": None,
                    "error": str(e),
                })
                logger.warning(f"[CalTesterInteractor] {key} 채점 실패 | error={e}")

        results.sort(key=lambda r: r.get("accuracy") or -1, reverse=True)
        for i, r in enumerate(results):
            r["rank"] = i + 1

        champion = results[0] if results else None
        logger.info(f"[CalTesterInteractor] 챔피언 결정 | {champion}")

        return {
            "test_samples": len(X_test),
            "champion": champion,
            "ranking": results,
        }
    
    async def analyze_message_intent(self, user_message: str) -> dict:
        '''사용자의 질문(message)을 형태소 분석하여 키워드와 의도를 파악한다'''
        logger.info(f"[JackTrainerInteractor] 전처리 및 분석 시작 | message: {user_message}")

        tokens = self.kiwi.tokenize(user_message)
        keywords = []
        has_quantity_modifier = False
        has_count_unit = False

        for t in tokens:
            if t.tag in ("NNG", "NNP"):
                keywords.append(t.form)
            if t.tag == "MM" and t.form == "몇":
                has_quantity_modifier = True
            if t.tag == "NNB" and t.form in ("명", "개", "사람", "분"):
                has_count_unit = True

        is_count_query = has_quantity_modifier or has_count_unit or ("몇" in user_message)
        analysis_result = {"keywords": keywords, "is_count_query": is_count_query}

        logger.info(f"[JackTrainerInteractor] 분석 완료 | 결과: {analysis_result}")
        return analysis_result

    async def introduce_myself(self, schema: CalTesterSchema) -> CalTesterResponse:
        '''칼 테스터의 자기소개 인터렉트'''
        return await self.repository.introduce_myself(CalTesterQuery(
            id=schema.id,
            name=schema.name,
        ))


# ── Helper ──────────────────────────────────────────────────────────────────────

def _preprocess_test(df: pd.DataFrame) -> tuple[list[list[float]], list[int]]:
    """테스트 데이터 전처리 → (X_test, y_test)

    Jack의 train_model과 동일한 피처 변환을 적용한다.
    FareBand는 테스트 셋 자체 분포로 qcut (Jack과 독립 적용).
    """
    test = df.copy()

    y_test = test["survived"].astype(int).tolist()
    test = test.drop("survived", axis=1)

    # 호칭 추출 및 Nominal 변환
    test["Title"] = test["name"].str.extract(r"([A-Za-z]+)\.", expand=False)
    test["Title"] = test["Title"].replace(
        ["Capt", "Col", "Don", "Dr", "Major", "Rev", "Jonkheer", "Dona", "Mme"], "Rare"
    )
    test["Title"] = test["Title"].replace(["Countess", "Lady", "Sir"], "Royal")
    test["Title"] = test["Title"].replace({"Mlle": "Mr", "Ms": "Miss"})
    title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Royal": 5, "Rare": 6}
    test["Title"] = test["Title"].map(title_mapping).fillna(0).astype(int)

    # 성별 Nominal 변환
    test["gender"] = test["gender"].map({"male": 0, "female": 1})

    # 나이 구간 Ordinal 변환
    bins = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
    age_labels = ["Unknown", "Baby", "Child", "Teenager", "Student", "Young Adult", "Adult", "Senior"]
    age_title_mapping = {
        0: "Unknown", 1: "Baby", 2: "Child", 3: "Teenager",
        4: "Student", 5: "Young Adult", 6: "Adult", 7: "Senior",
    }
    age_mapping = {v: k for k, v in age_title_mapping.items()}

    test["age"] = pd.to_numeric(test["age"], errors="coerce").fillna(-0.5)
    test["AgeGroup"] = pd.cut(test["age"], bins, labels=age_labels).astype(str)
    mask = test["AgeGroup"] == "Unknown"
    test.loc[mask, "AgeGroup"] = test.loc[mask, "Title"].map(age_title_mapping)
    test["AgeGroup"] = test["AgeGroup"].map(age_mapping).fillna(0).astype(int)

    # 승선항 Nominal 변환
    test["embarked"] = test["embarked"].fillna("S").map({"S": 1, "C": 2, "Q": 3})

    # 요금 Ordinal 변환
    test["fare"] = pd.to_numeric(test["fare"], errors="coerce").fillna(0)
    test["FareBand"] = (
        pd.qcut(test["fare"], 4, labels=[1, 2, 3, 4], duplicates="drop")
        .fillna(1).astype(int)
    )

    # 불필요 컬럼 드롭
    drop_cols = ["name", "age", "fare", "ticket", "cabin", "passenger_id"]
    test = test.drop(columns=[c for c in drop_cols if c in test.columns])

    return test.values.tolist(), y_test
