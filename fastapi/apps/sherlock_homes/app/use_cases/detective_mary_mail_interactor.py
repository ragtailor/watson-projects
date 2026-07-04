from __future__ import annotations

from sherlock_homes.adapter.inbound.api.schemas.detective_mary_mail_schema import MaryMailSchema, MaryMailReceiveSchema
from sherlock_homes.app.dtos.detective_mary_mail_dto import MaryMailQuery, MaryMailResponse, MaryMailReceiveQuery, MaryMailReceiveResponse
from sherlock_homes.app.ports.input.detective_mary_mail_use_case import MaryMailUseCase
from sherlock_homes.app.ports.output.detective_mary_mail_port import MaryMailPort
from tailor.core.lol.t1_mid_faker_orchestrator import FakerOrchestrator


class MaryMailInteractor(MaryMailUseCase):

    def __init__(self, repository: MaryMailPort, orchestrator: FakerOrchestrator):
        self.repository = repository
        self.orchestrator = orchestrator

    async def introduce_myself(self, schema: MaryMailSchema) -> MaryMailResponse:
        '''메리 왓슨의 자기소개 인터렉트'''
        return await self.repository.introduce_myself(MaryMailQuery(
            id=schema.id,
            name=schema.name
        ))

    async def receive_mail(self, schema: MaryMailReceiveSchema) -> MaryMailReceiveResponse:
        '''n8n 수신 메일 처리 인터렉트'''
        embedding = await self.orchestrator.embed(f"{schema.subject}\n{schema.preview}")
        return await self.repository.receive_mail(MaryMailReceiveQuery(
            subject=schema.subject,
            from_=schema.from_,
            to=schema.to,
            preview=schema.preview,
            message_id=schema.message_id,
            embedding=embedding
        ))
