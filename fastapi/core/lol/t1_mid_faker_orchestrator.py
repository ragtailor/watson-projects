import httpx

_OLLAMA_BASE_URL = "http://localhost:11434"
_EXAONE_MODEL = "exaone3.5:2.4b"


class FakerOrchestrator:
    def __init__(
        self,
        base_url: str = _OLLAMA_BASE_URL,
        model: str = _EXAONE_MODEL,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    async def chat(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
            )
            response.raise_for_status()
            return response.json()["message"]["content"]

    async def generate(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]


faker_orchestrator = FakerOrchestrator()
