from shared.domain.collectors.payloads import (
    WeatherCollectorPayloadIn,
    WeatherCollectorPayloadOut,
)

from loguru import logger as log
from fastapi import APIRouter, status, HTTPException

__all__ = ["router"]

router = APIRouter(prefix="/collectors", tags=["collectors"])


@router.get("/status", status_code=status.HTTP_200_OK)
def collectors_status():
    return {"status": "Collectors endpoint online"}


@router.post("/weather", status_code=status.HTTP_201_CREATED)
def receive_weather(payload: WeatherCollectorPayloadIn):
    log.debug(f"Received: {payload.source} | {payload.label} | {payload.data}")

    return {"message": "Data received"}
