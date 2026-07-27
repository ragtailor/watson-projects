from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from silicon_valley.adapter.inbound.api.schemas.graph_pdf_loader_schema import GraphPdfLoaderResultSchema
from silicon_valley.app.dtos.graph_pdf_loader_dto import GraphPdfLoaderCommand
from silicon_valley.app.ports.input.graph_pdf_loader_use_case import GraphPdfLoaderUseCase
from silicon_valley.dependencies.graph_pdf_loader_provider import get_graph_pdf_loader_use_case

'''
PDF 업로드 → 본문 추출(neo4j_graphrag PdfLoader) → 요약(Gemini) → 저장 파이프라인 라우터
'''
graph_pdf_loader_router = APIRouter(prefix="/pdf", tags=["pdf"])


@graph_pdf_loader_router.post(
    "/upload",
    response_model=GraphPdfLoaderResultSchema,
    summary="PDF 업로드 후 본문 추출·요약",
)
async def upload_pdf(
    file: UploadFile = File(...),
    use_case: GraphPdfLoaderUseCase = Depends(get_graph_pdf_loader_use_case),
) -> GraphPdfLoaderResultSchema:

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드할 수 있습니다.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")

    response = await use_case.upload(
        GraphPdfLoaderCommand(filename=file.filename, file_bytes=file_bytes)
    )

    return GraphPdfLoaderResultSchema(
        id=response.id,
        filename=response.filename,
        summary=response.summary,
    )
