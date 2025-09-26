from shared.domain.collectors.payloads import (
    WeatherCollectorPayloadIn,
    WeatherCollectorPayloadOut,
)
from shared.domain.weatherapi.weather import (
    CurrentWeatherIn,
    CurrentWeatherOut,
    ForecastJSONIn,
    ForecastJSONOut,
)
from shared.domain.weatherapi.location import LocationIn, LocationOut

from loguru import logger as log
from fastapi import APIRouter, status, HTTPException

__all__ = ["router"]

router = APIRouter(prefix="/collectors", tags=["collectors"])


@router.get("/status", status_code=status.HTTP_200_OK)
def collectors_status():
    return {"status": "Collectors endpoint online"}


@router.post("/weather", status_code=status.HTTP_201_CREATED)
def receive_weather(payload: WeatherCollectorPayloadIn):
    log.debug(
        f"Received: [source: {payload.source}] | [label: {payload.label}] | {payload.data}"
    )

    match payload.source:
        case "weatherapi":

            match payload.label:
                case "current":
                    location: LocationIn = LocationIn.model_validate(
                        payload.data["location"]
                    )
                    current_weather: CurrentWeatherIn = CurrentWeatherIn.model_validate(
                        payload.data["current"]
                    )
                    log.debug(f"Current weather object: {current_weather}")

                case _:
                    log.error(f"Invalid label: {payload.label}")
                    raise HTTPException(status_code=400, detail="Invalid label")

        case _:
            log.error(f"Invalid source: {payload.source}")
            raise HTTPException(status_code=400, detail="Invalid source")

    return {"message": "Data received"}
