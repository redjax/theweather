import typing as t
import json

from shared.domain.collectors.payloads import WeatherCollectorPayloadIn
from shared.domain.weatherapi.weather import (
    CurrentWeatherJSONIn,
    CurrentWeatherJSONModel,
    CurrentWeatherJSONRepository,
    CurrentWeatherIn,
    CurrentWeatherModel,
    CurrentWeatherRepository,
    ForecastJSONIn,
    ForecastJSONModel,
    ForecastJSONOut,
    ForecastJSONRepository,
)
from shared.domain.weatherapi.location import (
    LocationIn,
    LocationModel,
    LocationRepository,
)
from api_server.depends import get_db
from api_server.routers.v1.collectors._db import (
    save_weatherapi_current_weather,
    save_weatherapi_weather_forecast,
)

from loguru import logger as log
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import sqlalchemy.exc as sa_exc


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

        ## WeatherAPI collector data
        case "weatherapi":
            match payload.label:

                ## Current weather data
                case "current":
                    log.info(f"Received current weather from collector")

                    ## Attempt to save to database
                    try:
                        db_models: dict[
                            str,
                            t.Union[
                                LocationModel,
                                CurrentWeatherModel,
                                CurrentWeatherJSONModel,
                            ],
                        ] = save_weatherapi_current_weather(
                            data=payload.data.get("current"), session=db
                        )
                    except sa_exc.IntegrityError as exc:
                        log.error(f"Failed to save current weather to database: {exc}")
                        raise HTTPException(
                            status_code=409,
                            detail="Weather data already exists in database.",
                        )
                    except sa_exc.InternalError as internal_err:
                        log.error(
                            f"Failed to save current weather to database: {internal_err}"
                        )
                        raise HTTPException(
                            status_code=500,
                            detail="Database error occurred while saving data.",
                        )
                    except sa_exc.DBAPIError as db_err:
                        log.error(
                            f"Failed to save current weather to database: {db_err}"
                        )
                        raise HTTPException(
                            status_code=500,
                            detail="Database error occurred while saving data.",
                        )

                    ## Extract models from db save function return
                    db_current_weather = db_models["current_weather"]
                    db_current_weather_json = db_models["current_weather_json"]
                    db_location = db_models["location"]

                    return JSONResponse(
                        content={
                            "success": True,
                            "message": "Weather data saved to database.",
                            "location_id": db_location.id,
                            "current_weather_id": db_current_weather.id,
                            "current_weather_json_id": db_current_weather_json.id,
                        },
                        status_code=status.HTTP_201_CREATED,
                    )

                ## Forecast weather data
                case "forecast":
                    log.info(f"Received forecast weather from collector")

                    ## Attempt to parse the incoming JSON data
                    try:
                        data_dict = payload.data
                        forecast_data = data_dict.get("forecast_json")
                        if not forecast_data:
                            raise ValueError("Missing 'forecast_json' key in data")
                    except (json.JSONDecodeError, ValueError) as e:
                        log.error(f"Invalid JSON data: {e}")
                        raise HTTPException(status_code=400, detail="Invalid JSON data")

                    ## Attempt to save to database
                    try:
                        db_models: dict[
                            str,
                            t.Union[
                                LocationModel,
                                ForecastJSONModel,
                            ],
                        ] = save_weatherapi_weather_forecast(
                            data=payload.data, session=db
                        )
                    except sa_exc.IntegrityError as exc:
                        log.error(f"Failed to save current weather to database: {exc}")
                        raise HTTPException(
                            status_code=409,
                            detail="Weather data already exists in database.",
                        )
                    except sa_exc.InternalError as internal_err:
                        log.error(
                            f"Failed to save current weather to database: {internal_err}"
                        )
                        raise HTTPException(
                            status_code=500,
                            detail="Database error occurred while saving data.",
                        )
                    except sa_exc.DBAPIError as db_err:
                        log.error(
                            f"Failed to save current weather to database: {db_err}"
                        )
                        raise HTTPException(
                            status_code=500,
                            detail="Database error occurred while saving data.",
                        )

                    ## Extract models from db save function return
                    db_weather_forecast_json = db_models["forecast_json"]
                    db_location = db_models["location"]

                    return JSONResponse(
                        content={
                            "success": True,
                            "message": "Weather data saved to database.",
                            "location_id": db_location.id,
                            "weather_forecast_json": db_weather_forecast_json.id,
                        },
                        status_code=status.HTTP_201_CREATED,
                    )

                ## Invalid collector data label
                case _:
                    log.error(f"Invalid label: {payload.label}")
                    raise HTTPException(status_code=400, detail="Invalid label")

        ## Invalid collector
        case _:
            log.error(f"Invalid source: {payload.source}")
            raise HTTPException(status_code=400, detail="Invalid source")
