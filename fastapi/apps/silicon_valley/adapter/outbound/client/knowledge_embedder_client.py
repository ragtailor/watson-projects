from __future__ import annotations

import os

import httpx

from silicon_valley.app.ports.output.knowledge_embedder_port import KnowledgeEmbedderPort

# 채팅 모델(OLLAMA_MODEL)과 별개다. exaone3.5:2.4b 같은 completion 모델은
# Ollama가 임베딩 모드로 기동하지 않아 /api/embeddings가 동작하지 않는다.
_OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
_OLLAMA_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")


class KnowledgeEmbedderClient(KnowledgeEmbedderPort):
    '''Ollama /api/embeddings로 문서 조각을 임베딩한다.'''

    def __init__(
        self,
        base_url: str = _OLLAMA_BASE_URL,
        model: str = _OLLAMA_EMBED_MODEL,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await self._embed_one(client, text)

    async def embed_all(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return [await self._embed_one(client, text) for text in texts]

    async def _embed_one(self, client: httpx.AsyncClient, text: str) -> list[float]:
        response = await client.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text},
        )
        response.raise_for_status()
        payload = response.json()

        embedding = payload.get("embedding")
        if not embedding:
            raise RuntimeError(
                f"임베딩 생성에 실패했습니다 (model={self.model}): {payload.get('error', payload)}"
            )

        return embedding
