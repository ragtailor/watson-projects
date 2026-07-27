from __future__ import annotations

import tempfile
from pathlib import Path

from neo4j_graphrag.experimental.components.pdf_loader import PdfLoader

from silicon_valley.app.ports.output.graph_pdf_extractor_port import GraphPdfExtractorPort


class GraphPdfExtractor(GraphPdfExtractorPort):
    '''neo4j_graphrag의 PdfLoader로 업로드된 PDF 바이너리에서 본문 텍스트를 추출한다.'''

    def __init__(self) -> None:
        self._loader = PdfLoader()

    async def extract_text(self, filename: str, file_bytes: bytes) -> str:
        suffix = Path(filename).suffix or ".pdf"
        with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            document = await self._loader.run(filepath=Path(tmp.name))

        return document.text
