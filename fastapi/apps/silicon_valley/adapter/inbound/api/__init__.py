from fastapi import APIRouter

from silicon_valley.adapter.inbound.api.v1.piper_gilfoyle_llm_router import gilfoyle_llm_router
from silicon_valley.adapter.inbound.api.v1.graph_pdf_loader_router import graph_pdf_loader_router
from silicon_valley.adapter.inbound.api.v1.morningstar_insight_router import morningstar_insight_router
from silicon_valley.adapter.inbound.api.v1.piper_monica_graph_router import monica_graph_router
from silicon_valley.adapter.inbound.api.v1.s3_image_upload_router import s3_image_upload_router

# 피드 파이퍼 멤버 자기소개 라우터 (GET /{멤버}/myself)
from silicon_valley.adapter.inbound.api.v1.piper_bighetti_hr_router import bighetti_hr_router
from silicon_valley.adapter.inbound.api.v1.piper_dinesh_dash_router import dinesh_dash_router
from silicon_valley.adapter.inbound.api.v1.piper_dunn_coo_router import dunn_coo_router
from silicon_valley.adapter.inbound.api.v1.piper_gilfoyle_sys_router import gilfoyle_sys_router
from silicon_valley.adapter.inbound.api.v1.piper_henricks_ceo_router import henricks_ceo_router

silicon_valley_router = APIRouter(prefix="/silicon-valley", tags=["silicon-valley"])

silicon_valley_router.include_router(gilfoyle_llm_router)
silicon_valley_router.include_router(graph_pdf_loader_router)
silicon_valley_router.include_router(morningstar_insight_router)
silicon_valley_router.include_router(monica_graph_router)

# gilfoyle_sys_router는 gilfoyle_llm_router와 prefix(/gilfoyle)가 같다.
# 경로가 /myself vs /llm/generate 로 갈리므로 충돌하지 않는다.
silicon_valley_router.include_router(bighetti_hr_router)
silicon_valley_router.include_router(dinesh_dash_router)
silicon_valley_router.include_router(dunn_coo_router)
silicon_valley_router.include_router(gilfoyle_sys_router)
silicon_valley_router.include_router(henricks_ceo_router)
