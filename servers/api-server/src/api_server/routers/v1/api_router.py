from fastapi import APIRouter

__all__ = ["api_v1_router"]

api_v1_router = APIRouter(prefix="/v1")


@api_v1_router.get("/status")
def v1_status():
    return {"status": "API v1 online"}
