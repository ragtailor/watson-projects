from __future__ import annotations

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame

from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schema import HartleyViolinSchema
from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinQuery, HartleyViolinResponse
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.output.crew_hartley_violin_port import HartleyViolinPort


class HartleyViolinInteractor(HartleyViolinUseCase):

    def __init__(self, repository: HartleyViolinPort):
        self.repository = repository

    async def introduce_myself(self, schema: HartleyViolinSchema) -> HartleyViolinResponse:
        return await self.repository.introduce_myself(HartleyViolinQuery(
            id=schema.id,
            name=schema.name,
        ))

    _TITLE_MAPPING = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Royal": 5, "Rare": 6}
    _RARE_TITLES  = {"Capt", "Col", "Don", "Dr", "Major", "Rev", "Jonkheer", "Dona", "Mme"}
    _ROYAL_TITLES = {"Countess", "Lady", "Sir"}
    _TITLE_ALIAS  = {"Mlle": "Mr", "Ms": "Miss"}

    _FEATURES = [
        "survived", "pclass", "age", "sibsp", "parch", "fare",
        "gender", "embarked_code", "family_size", "title",
    ]

    def get_correlation_chart(self, df: DataFrame) -> bytes:
        df = df.copy()
        self._encode_gender(df)
        self._encode_embarked(df)
        self._encode_family_size(df)
        self._encode_title(df)

        cols = [c for c in self._FEATURES if c in df.columns]
        corr_matrix = df[cols].corr()

        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
        ax.set_title("Titanic Data Correlation (10 features)")

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        plt.close(fig)

        return buffer.getvalue()

    @staticmethod
    def _encode_gender(df: DataFrame) -> None:
        if "sex" in df.columns:
            df["gender"] = df["sex"].map({"male": 0, "female": 1})

    @staticmethod
    def _encode_embarked(df: DataFrame) -> None:
        if "embarked" in df.columns:
            df["embarked_code"] = df["embarked"].map({"S": 0, "C": 1, "Q": 2})

    @staticmethod
    def _encode_family_size(df: DataFrame) -> None:
        if "sibsp" in df.columns and "parch" in df.columns:
            df["family_size"] = df["sibsp"] + df["parch"] + 1

    def _encode_title(self, df: DataFrame) -> None:
        import re

        def _title_from_name(name: str) -> int:
            m = re.search(r"([A-Za-z]+)\.", str(name))
            if not m:
                return 0
            raw = self._TITLE_ALIAS.get(m.group(1), m.group(1))
            if raw in self._RARE_TITLES:
                return self._TITLE_MAPPING["Rare"]
            if raw in self._ROYAL_TITLES:
                return self._TITLE_MAPPING["Royal"]
            return self._TITLE_MAPPING.get(raw, 0)

        if "name" in df.columns:
            df["title"] = df["name"].apply(_title_from_name)
        elif "who" in df.columns:
            df["title"] = df["who"].map({"man": 1, "woman": 2, "child": 4})
