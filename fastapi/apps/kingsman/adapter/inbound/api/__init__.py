from fastapi import APIRouter

from kingsman.adapter.inbound.api.v1.oauth_router import oauth_router

kingsman_router = APIRouter(prefix="/kingsman", tags=["kingsman"])
kingsman_router.include_router(oauth_router)
