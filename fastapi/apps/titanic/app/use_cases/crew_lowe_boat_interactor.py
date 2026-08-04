from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from titanic.adapter.inbound.api.schemas.crew_lowe_boat_schema import LoweBoatSchema
from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery, LoweBoatResponse
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.ports.output.crew_lowe_boat_port import LoweBoatPort

logger = logging.getLogger(__name__)


class LoweBoatInteractor(LoweBoatUseCase):

    def __init__(self, repository: LoweBoatPort):
        self.repository = repository

    
    def feature_engineering(self, train_set):
        train = train_set.copy()

        # 1. Label 분리
        y_label = train["survived"].astype(int).tolist()
        train = train.drop("survived", axis=1)

        # 2. 호칭 추출 및 Nominal 변환
        train["Title"] = train["name"].str.extract(r"([A-Za-z]+)\.", expand=False)
        train["Title"] = train["Title"].replace(
            ["Capt", "Col", "Don", "Dr", "Major", "Rev", "Jonkheer", "Dona", "Mme"], "Rare"
        )
        train["Title"] = train["Title"].replace(["Countess", "Lady", "Sir"], "Royal")
        train["Title"] = train["Title"].replace({"Mlle": "Mr", "Ms": "Miss"})
        title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Royal": 5, "Rare": 6}
        train["Title"] = train["Title"].map(title_mapping).fillna(0).astype(int)

        # 3. 성별 Nominal 변환 (female=1, male=0)
        train["gender"] = train["gender"].map({"male": 0, "female": 1})

        # 4. 나이 구간 Ordinal 변환 및 결측치 처리
        bins = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
        age_labels = ["Unknown", "Baby", "Child", "Teenager", "Student", "Young Adult", "Adult", "Senior"]
        age_title_mapping = {
            0: "Unknown", 1: "Baby", 2: "Child", 3: "Teenager",
            4: "Student", 5: "Young Adult", 6: "Adult", 7: "Senior",
        }
        age_mapping = {v: k for k, v in age_title_mapping.items()}

        train["age"] = pd.to_numeric(train["age"], errors="coerce").fillna(-0.5)
        train["AgeGroup"] = pd.cut(train["age"], bins, labels=age_labels).astype(str)
        mask = train["AgeGroup"] == "Unknown"
        train.loc[mask, "AgeGroup"] = train.loc[mask, "Title"].map(age_title_mapping)
        train["AgeGroup"] = train["AgeGroup"].map(age_mapping).fillna(0).astype(int)

        # 5. 승선항 Nominal 변환
        train["embarked"] = train["embarked"].fillna("S").map({"S": 1, "C": 2, "Q": 3})

        # 6. 요금 Ordinal 변환 (train 기준 4분위 구간 정의)
        train["fare"] = pd.to_numeric(train["fare"], errors="coerce").fillna(0)
        train["FareBand"] = (
            pd.qcut(train["fare"], 4, labels=[1, 2, 3, 4], duplicates="drop")
            .fillna(1).astype(int)
        )

        # 7. 불필요 컬럼 드롭
        drop_cols = ["name", "age", "fare", "ticket", "cabin", "passenger_id"]
        train = train.drop(columns=[c for c in drop_cols if c in train.columns])


    async def introduce_myself(self, schema: LoweBoatSchema) -> LoweBoatResponse:
        '''로우 보트의 자기소개 인터랙트'''
        return await self.repository.introduce_myself(LoweBoatQuery(
            id=schema.id,
            name=schema.name,
        ))


