from shared.domain.collectors.payloads import (
    WeatherCollectorPayloadIn,
    WeatherCollectorPayloadOut,
)

from loguru import logger as log
from fastapi import APIRouter, status, HTTPException

__all__ = ["collectors_router"]

collectors_router = APIRouter(prefix="/v1", tags=["collectors"])


@collectors_router.post("/weather", status_code=status.HTTP_201_CREATED)
def receive_weather(payload: WeatherCollectorPayloadIn):
    log.debug(f"Received: {payload.source} | {payload.label} | {payload.data}")

    return {"message": "Data received"}
