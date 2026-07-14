from fastapi import APIRouter

from silicon_valley.adapter.inbound.api.v1.piper_gilfoyle_llm_router import gilfoyle_llm_router

silicon_valley_router = APIRouter(prefix="/silicon-valley", tags=["silicon-valley"])

silicon_valley_router.include_router(gilfoyle_llm_router)
