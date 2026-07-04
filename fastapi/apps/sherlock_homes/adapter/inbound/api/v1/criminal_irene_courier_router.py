from fastapi import APIRouter, Depends

from sherlock_homes.adapter.inbound.api.schemas.irene_courier_schema import IreneCourierSchema
from sherlock_homes.app.dtos.irene_courier_dto import IreneCourierResponse
from sherlock_homes.app.ports.input.irene_courier_use_case import IreneCourierUseCase
from sherlock_homes.dependencies.irene_courier_provider import get_irene_courier_use_case

'''
아이린 애들러 (Irene Adler)
역할 (keyword): courier (전령)
드라마 설정 및 시스템 기능: 셜록이 유일하게 "그 여자"라 부르는 인물.
치밀한 언어와 문장으로 상대를 압도하며, LLM이 작성한 이메일을 지정된 수신자에게 발송합니다.
'''

irene_courier_router = APIRouter(prefix="/irene", tags=["irene"])


@irene_courier_router.post("/send")
async def send_email(
    schema: IreneCourierSchema,
    irene: IreneCourierUseCase = Depends(get_irene_courier_use_case)
) -> IreneCourierResponse:
    return await irene.send_email(schema)
