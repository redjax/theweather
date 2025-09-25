from api_server.routers.v1.collectors import collectors_router

from fastapi import APIRouter

__all__ = ["api_v1_router"]

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(collectors_router)


@api_v1_router.get("/status")
def v1_status():
    return {"status": "API v1 online"}
