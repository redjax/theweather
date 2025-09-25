from api_server.routers.v1 import v1_router

from fastapi import APIRouter, status

__all__ = ["router"]

router = APIRouter(prefix="/api")

router.include_router(v1_router.api_v1_router)
