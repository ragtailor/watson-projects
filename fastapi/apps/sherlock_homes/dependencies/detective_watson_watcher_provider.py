from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from sherlock_homes.adapter.outbound.repositories.detective_watson_watcher_repository import WatsonWatcherRepository
from sherlock_homes.app.ports.output.detective_watson_watcher_port import WatsonWatcherPort
from core.matrix.grid_oracle_database_manager import get_db
from sherlock_homes.app.ports.input.detective_watson_watcher_use_case import WatsonWatcherUseCase
from sherlock_homes.app.use_cases.detective_watson_watcher_interactor import WatsonWatcherInteractor

'''
캐릭터: 존 왓슨 (John)
역할 (keyword): watcher (관찰/기록자)
드라마 설정 및 시스템 기능: 셜록의 파트너인 사설 탐정 조력자.
셜록의 모든 추론 과정을 블로그에 기록하듯, 시스템의 이벤트·로그·상태 변화를 관찰하고 기록합니다.
'''

def get_watson_watcher_use_case(
        db: AsyncSession = Depends(get_db)
) -> WatsonWatcherUseCase:
    repository: WatsonWatcherPort = WatsonWatcherRepository(session=db)
    return WatsonWatcherInteractor(repository=repository)
