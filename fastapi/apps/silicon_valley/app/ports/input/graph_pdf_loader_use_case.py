from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.graph_pdf_loader_dto import GraphPdfLoaderCommand, GraphPdfLoaderResponse


class GraphPdfLoaderUseCase(ABC):

    @abstractmethod
    async def upload(self, command: GraphPdfLoaderCommand) -> GraphPdfLoaderResponse:
        '''PDF를 업로드받아 텍스트 추출→요약→저장까지 수행하는 메소드'''
        pass
