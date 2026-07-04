from fastapi import APIRouter, Depends

from sherlock_homes.adapter.inbound.api.schemas.detective_mary_mail_schema import MaryMailSchema, MaryMailReceiveSchema
from sherlock_homes.app.dtos.detective_mary_mail_dto import MaryMailResponse, MaryMailReceiveResponse
from sherlock_homes.app.ports.input.detective_mary_mail_use_case import MaryMailUseCase
from sherlock_homes.dependencies.detective_mary_mail_provider import get_mary_mail_use_case

'''
메리 왓슨 (Mary)
역할 (keyword): mail (메일/알림)
사설 탐정단에 합류한 전직 비밀 요원.
베이커가 팀의 소식을 전하듯, 시스템 내부의 이메일 발송, 알림 전달 및 메시지 처리를 수행합니다.
'''

mary_mail_router = APIRouter(prefix="/mary", tags=["mary"])


@mary_mail_router.get("/myself")
async def introduce_myself(
    mary: MaryMailUseCase = Depends(get_mary_mail_use_case)
) -> MaryMailResponse:
    return await mary.introduce_myself(
        MaryMailSchema(
            id=12,
            name="메리 왓슨 (Mary)"
        )
    )


@mary_mail_router.post("/receive")
async def receive_mail(
    schema: MaryMailReceiveSchema,
    mary: MaryMailUseCase = Depends(get_mary_mail_use_case)
) -> MaryMailReceiveResponse:
    # 여기에 들어오면 로그를 작성해줘.
    # 여기에 들어오면 텔레그램으로 전송해줘.
    return await mary.receive_mail(schema)
