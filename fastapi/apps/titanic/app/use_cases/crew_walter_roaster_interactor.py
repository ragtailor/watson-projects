from typing import Any

import pandas as pd

from titanic.adapter.inbound.api.schemas.crew_walter_roaster_schema import WalterRoasterSchema
from titanic.app.dtos.crew_walter_roaster_dto import WalterRoasterQuery, WalterRoasterResponse
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.ports.output.crew_walter_roaster_port import WalterRoasterPort


class WalterQuery:
    def __init__(self, repository) -> None:
        self.repository = repository

    async def list_paginated(self, page: int, page_size: int) -> dict[str, Any]:
        total, items = await self.repository.list_paginated(page, page_size)
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items,
        }


class WalterRoasterInteractor(WalterRoasterUseCase):

    def __init__(self, repository: WalterRoasterPort) -> None:
        self.repository = repository

    def get_train_set(self) -> pd.DataFrame:
        '''월터가 DB에서 train set 만 가져오는 메소드'''
        return self.repository.get_train_set()

    def get_test_set(self) -> pd.DataFrame:
        '''월터가 DB에서 test set 만 가져오는 메소드'''
        return self.repository.get_test_set()

    async def introduce_myself(self, schema: WalterRoasterSchema) -> WalterRoasterResponse:
        return await self.repository.introduce_myself(WalterRoasterQuery(
            id=schema.id,
            name=schema.name,
            memo=schema.memo,
        ))
