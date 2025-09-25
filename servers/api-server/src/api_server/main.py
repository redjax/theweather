from api_server.routers import health
from api_server.routers import api_router
from api_server.config import FASTAPI_SETTINGS

from fastapi import FastAPI

__all__ = ["app"]

app = FastAPI(
    title=FASTAPI_SETTINGS.get("TITLE", "Unnamed Server"),
    description=FASTAPI_SETTINGS.get("DESCRIPTION", "No description"),
    version=FASTAPI_SETTINGS.get("VERSION", "0.1.0"),
    debug=FASTAPI_SETTINGS.get("DEBUG", False),
    root_path=FASTAPI_SETTINGS.get("ROOT_PATH", "/"),
    openapi_url=FASTAPI_SETTINGS.get("OPENAPI_URL", "/openapi.json"),
)

app.include_router(health.router)
app.include_router(api_router.router)


if __name__ == "__main__":
    pass
