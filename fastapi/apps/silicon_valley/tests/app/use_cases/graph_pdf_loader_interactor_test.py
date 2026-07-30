import pytest

from silicon_valley.app.dtos.graph_pdf_loader_dto import GraphPdfLoaderCommand
from silicon_valley.app.use_cases.graph_pdf_loader_interactor import GraphPdfLoaderInteractor
from silicon_valley.domain.document_vector import DocumentVector
from silicon_valley.domain.knowledge_chunk import KnowledgeChunk

_EMBEDDING_DIM = 768


class _FakeExtractor:
    def __init__(self, text: str) -> None:
        self.text = text

    async def extract_text(self, filename: str, file_bytes: bytes) -> str:
        return self.text


class _FakeSummarizer:
    async def summarize(self, text: str) -> str:
        return f"요약({len(text)}자)"


class _FakeDocumentRepository:
    def __init__(self) -> None:
        self.saved: list[DocumentVector] = []

    async def save(self, filename: str, content: str, summary: str) -> DocumentVector:
        document = DocumentVector(id=42, filename=filename, content=content, summary=summary)
        self.saved.append(document)
        return document


class _FakeEmbedder:
    def __init__(self) -> None:
        self.embedded: list[str] = []

    async def embed(self, text: str) -> list[float]:
        self.embedded.append(text)
        return [float(len(text))] * _EMBEDDING_DIM

    async def embed_all(self, texts: list[str]) -> list[list[float]]:
        return [await self.embed(text) for text in texts]


class _FakeChunkRepository:
    def __init__(self) -> None:
        self.rows: list[tuple[int, int, str, list[float]]] = []

    async def save_all(self, document_id, contents, embeddings) -> int:
        if len(contents) != len(embeddings):
            raise ValueError("조각 수와 임베딩 수가 일치하지 않습니다.")
        for index, (content, embedding) in enumerate(zip(contents, embeddings)):
            self.rows.append((document_id, index, content, embedding))
        return len(self.rows)

    async def search_similar(self, embedding, limit) -> list[KnowledgeChunk]:
        return [
            KnowledgeChunk(id=i + 1, document_id=d, chunk_index=idx, content=c)
            for i, (d, idx, c, _) in enumerate(self.rows[:limit])
        ]


def _make_interactor(text: str):
    embedder = _FakeEmbedder()
    chunk_repository = _FakeChunkRepository()
    interactor = GraphPdfLoaderInteractor(
        extractor=_FakeExtractor(text),
        summarizer=_FakeSummarizer(),
        repository=_FakeDocumentRepository(),
        embedder=embedder,
        chunk_repository=chunk_repository,
    )
    return interactor, embedder, chunk_repository


_COMMAND = GraphPdfLoaderCommand(filename="report.pdf", file_bytes=b"%PDF-1.4 fake")


async def test_업로드하면_조각이_적재된다():
    interactor, _, chunk_repository = _make_interactor("본문 내용. " * 400)

    response = await interactor.upload(_COMMAND)

    assert response.chunk_count > 0
    assert len(chunk_repository.rows) == response.chunk_count


async def test_조각마다_임베딩이_하나씩_생성된다():
    interactor, embedder, chunk_repository = _make_interactor("본문 내용. " * 400)

    response = await interactor.upload(_COMMAND)

    assert len(embedder.embedded) == response.chunk_count
    for _, _, _, embedding in chunk_repository.rows:
        assert len(embedding) == _EMBEDDING_DIM


async def test_조각은_저장된_문서_id로_연결된다():
    interactor, _, chunk_repository = _make_interactor("본문 내용. " * 400)

    response = await interactor.upload(_COMMAND)

    assert all(document_id == response.id for document_id, _, _, _ in chunk_repository.rows)


async def test_chunk_index는_0부터_순차적이다():
    interactor, _, chunk_repository = _make_interactor("본문 내용. " * 400)

    await interactor.upload(_COMMAND)

    indexes = [index for _, index, _, _ in chunk_repository.rows]
    assert indexes == list(range(len(indexes)))


async def test_기존_요약_저장_동작은_유지된다():
    interactor, _, _ = _make_interactor("본문")

    response = await interactor.upload(_COMMAND)

    assert response.id == 42
    assert response.filename == "report.pdf"
    assert response.summary == "요약(2자)"


async def test_빈_본문이면_조각을_적재하지_않는다():
    interactor, embedder, chunk_repository = _make_interactor("   ")

    response = await interactor.upload(_COMMAND)

    assert response.chunk_count == 0
    assert chunk_repository.rows == []
    assert embedder.embedded == []
