from api_server.routers import health
from api_server.routers.v1 import api_v1_router
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
app.include_router(api_v1_router)


@app.get("/")
def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    pass
