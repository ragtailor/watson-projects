from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from lion_king.adapter.outbound.pg.outcast_scar_chatbot_pg_repository import ScarChatbotPgRepository
from lion_king.app.ports.output.outcast_scar_chatbot_repository import ScarChatbotRepository
from core.matrix.grid_oracle_database_manager import get_db
from lion_king.app.ports.input.outcast_scar_chatbot_use_case import ScarChatbotUseCase
from lion_king.app.use_cases.outcast_scar_chatbot_interactor import ScarChatbotInteractor


def get_scar_chatbot_repository(
        db: AsyncSession = Depends(get_db)
) -> ScarChatbotRepository:

    return ScarChatbotPgRepository(session=db)


def get_scar_chatbot_use_case(
        repository: ScarChatbotRepository = Depends(get_scar_chatbot_repository)
) -> ScarChatbotUseCase:

    return ScarChatbotInteractor(repository=repository)
