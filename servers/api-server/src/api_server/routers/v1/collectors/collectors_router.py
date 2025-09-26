from shared.domain.collectors.payloads import WeatherCollectorPayloadIn
from shared.domain.weatherapi.weather import (
    CurrentWeatherIn,
    CurrentWeatherOut,
    CurrentWeatherModel,
    CurrentWeatherRepository,
    ForecastJSONIn,
    ForecastJSONOut,
    ForecastJSONModel,
    ForecastJSONRepository,
)
from shared.domain.weatherapi.location import (
    LocationIn,
    LocationOut,
    LocationModel,
    LocationRepository,
)
from api_server.depends import get_db

from loguru import logger as log
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

__all__ = ["router"]

router = APIRouter(prefix="/collectors", tags=["collectors"])


@router.get("/status", status_code=status.HTTP_200_OK)
def collectors_status():
    return {"status": "Collectors endpoint online"}


@router.post("/weather", status_code=status.HTTP_201_CREATED)
def receive_weather(payload: WeatherCollectorPayloadIn, db: Session = Depends(get_db)):
    log.debug(
        f"Received: [source: {payload.source}] | [label: {payload.label}] | {payload.data}"
    )

    match payload.source:
        ## WeatherAPI
        case "weatherapi":

            match payload.label:
                ## Current weather
                case "current":
                    location: LocationIn = LocationIn.model_validate(
                        payload.data["location"]
                    )
                    current_weather: CurrentWeatherIn = CurrentWeatherIn.model_validate(
                        payload.data["current"]
                    )
                    log.debug(f"Current weather object: {current_weather}")

                    location_model: LocationModel = LocationModel(
                        **location.model_dump()
                    )
                    log.debug(f"Location model: {location_model.__dict__}")

                    current_weather_model: CurrentWeatherModel = CurrentWeatherModel(
                        **current_weather.model_dump()
                    )
                    log.debug(
                        f"Current weather model: {current_weather_model.__dict__}"
                    )

                case _:
                    log.error(f"Invalid label: {payload.label}")
                    raise HTTPException(status_code=400, detail="Invalid label")

        case _:
            log.error(f"Invalid source: {payload.source}")
            raise HTTPException(status_code=400, detail="Invalid source")

    return {"message": "Data received"}
