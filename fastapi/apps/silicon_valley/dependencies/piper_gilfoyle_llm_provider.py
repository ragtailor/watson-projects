import os

from fastapi import Depends

from silicon_valley.adapter.outbound.client.piper_gilfoyle_llm_client import GilfoyleLlmClient
from silicon_valley.app.ports.input.piper_gilfoyle_llm_use_case import GilfoyleLlmUseCase
from silicon_valley.app.ports.output.piper_gilfoyle_llm_port import GilfoyleLlmPort
from silicon_valley.app.use_cases.piper_gilfoyle_llm_interactor import GilfoyleLlmInteractor

EXAONE_SERVER_URL = os.environ.get("EXAONE_SERVER_URL", "http://127.0.0.1:8001")


def get_gilfoyle_llm_client() -> GilfoyleLlmPort:
    return GilfoyleLlmClient(base_url=EXAONE_SERVER_URL)


def get_gilfoyle_llm_use_case(
        client: GilfoyleLlmPort = Depends(get_gilfoyle_llm_client)
) -> GilfoyleLlmUseCase:

    return GilfoyleLlmInteractor(client=client)
