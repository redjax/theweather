"""Add a health check."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

router = APIRouter(tags=["status"], responses={404: {"description": "Not found"}})


class EndpointFilter(logging.Filter):
    """Filter pings to /health.

    https://stackoverflow.com/a/70810102
    """

    def filter(self, record: logging.LogRecord) -> bool:
        return record.args and len(record.args) >= 3 and record.args[2] != "/health"


## Add "healthy" ping filter to logger, don't log healthchecks
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


@router.get("/health", summary="Healthcheck")
async def healthy() -> JSONResponse:
    """Respond to healthchecks.

    Endpoint does not take any parameters or request bodies.

    Response: a 200 'OK', with a response body containing 'healthy'.
    """
    health: dict = jsonable_encoder({"healthy": True})
    response = JSONResponse(
        status_code=status.HTTP_200_OK, headers={"X-HEALTHY": "true"}, content=health
    )
    return response
