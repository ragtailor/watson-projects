from fastapi import APIRouter

from silicon_valley.adapter.inbound.api.v1.piper_gilfoyle_llm_router import gilfoyle_llm_router
from silicon_valley.adapter.inbound.api.v1.graph_pdf_loader_router import graph_pdf_loader_router
from silicon_valley.adapter.inbound.api.v1.morningstar_insight_router import morningstar_insight_router
from silicon_valley.adapter.inbound.api.v1.piper_monica_graph_router import monica_graph_router

silicon_valley_router = APIRouter(prefix="/silicon-valley", tags=["silicon-valley"])

silicon_valley_router.include_router(gilfoyle_llm_router)
silicon_valley_router.include_router(graph_pdf_loader_router)
silicon_valley_router.include_router(morningstar_insight_router)
silicon_valley_router.include_router(monica_graph_router)
