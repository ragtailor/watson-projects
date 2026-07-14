import httpx

from silicon_valley.app.dtos.piper_gilfoyle_llm_dto import GilfoyleLlmQuery, GilfoyleLlmResponse
from silicon_valley.app.ports.output.piper_gilfoyle_llm_port import GilfoyleLlmPort

'''
버트람 길포일 (Bertram Gilfoyle)
클라우드를 불신하고 직접 서버를 굴리는 시스템 아키텍트답게, 로컬에서 띄운
EXAONE 추론 서버(serve_exaone.py, GPU 전용 venv)에 HTTP로 위임한다.
'''


class GilfoyleLlmClient(GilfoyleLlmPort):

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def generate(self, query: GilfoyleLlmQuery) -> GilfoyleLlmResponse:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/generate",
                json={
                    "prompt": query.prompt,
                    "max_new_tokens": query.max_new_tokens,
                    "temperature": query.temperature,
                },
            )
            response.raise_for_status()
            return GilfoyleLlmResponse(response=response.json()["response"])
