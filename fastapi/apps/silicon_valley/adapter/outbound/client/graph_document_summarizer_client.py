from __future__ import annotations

from core.matrix.vault_keymaker_secret_manager import get_keymaker

from silicon_valley.app.ports.output.graph_document_summarizer_port import GraphDocumentSummarizerPort

_SUMMARY_PROMPT = "다음 문서를 한국어로 핵심 위주로 간결하게 요약해줘.\n\n{text}"


class GraphDocumentSummarizerClient(GraphDocumentSummarizerPort):
    '''Gemini로 추출된 본문 텍스트를 요약한다.'''

    def __init__(self) -> None:
        self._keymaker = get_keymaker()

    async def summarize(self, text: str) -> str:
        model = self._keymaker.get_gemini_model()
        if model is None:
            raise RuntimeError("GEMINI_API_KEY가 설정되지 않아 요약을 생성할 수 없습니다.")

        response = await model.generate_content_async(_SUMMARY_PROMPT.format(text=text))
        return response.text
