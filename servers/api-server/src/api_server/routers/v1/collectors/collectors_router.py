from shared.domain.collectors.payloads import WeatherCollectorPayloadIn
from shared.domain.weatherapi.weather import (
    CurrentWeatherJSONIn,
    CurrentWeatherJSONOut,
    CurrentWeatherJSONModel,
    CurrentWeatherJSONRepository,
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

    ## Determine what to do with incoming data based on source
    match payload.source:

        ## WeatherAPI
        case "weatherapi":

            ## Determine data type
            match payload.label:

                ## Current weather
                case "current":
                    log.info(f"Received current weather from collector")

                    ## Current weather raw JSON schema
                    raw_json: CurrentWeatherJSONIn = CurrentWeatherJSONIn(
                        current_weather_json=payload.data
                    )
                    # log.debug(f"Current weather JSON object: {current_weather_json}")

                    ## Location schema
                    location: LocationIn = LocationIn.model_validate(
                        payload.data["location"]
                    )
                    log.debug(f"Location object: {location}")

                    ## Current weather schema
                    current_weather: CurrentWeatherIn = CurrentWeatherIn.model_validate(
                        payload.data["current"]
                    )
                    log.debug(f"Current weather object: {current_weather}")

                    ## Current weather raw JSON model
                    current_weather_json_model: CurrentWeatherJSONModel = (
                        CurrentWeatherJSONModel(
                            current_weather_json=raw_json.current_weather_json
                        )
                    )

                    ## Location DB model
                    location_model: LocationModel = LocationModel(
                        **location.model_dump()
                    )
                    log.debug(f"Location model: {location_model.__dict__}")

                    ## Current weather DB model
                    current_weather_model: CurrentWeatherModel = (
                        current_weather.to_orm()
                    )

                    log.debug(
                        f"Current weather model: {current_weather_model.__dict__}"
                    )

                    ## Create DB repos
                    log.info(f"Saving location & current weather to database")
                    current_weather_json_repository = CurrentWeatherJSONRepository(db)
                    location_repository = LocationRepository(db)
                    current_weather_repository = CurrentWeatherRepository(db)

                    ## Save raw JSON
                    log.debug(f"Save current weather JSON")
                    try:
                        db_current_weather_json: CurrentWeatherJSONModel = (
                            current_weather_json_repository.create(
                                current_weather_json_model
                            )
                        )
                    except Exception as exc:
                        log.error(f"Error saving current weather JSON: {exc}")
                        raise HTTPException(
                            status_code=400, detail="Error saving current weather JSON"
                        )

                    ## Save location
                    log.debug(f"Save location")
                    try:
                        db_location: LocationModel = location_repository.save(
                            location_model
                        )
                    except Exception as exc:
                        log.error(f"Error saving location: {exc}")
                        raise HTTPException(
                            status_code=400, detail="Error saving location"
                        )

                    ## Save current weather

                    ## Extract location ID from saved model
                    current_weather_model.location_id = db_location.id

                    ## Extract dicts of weather, condition, & air quality data
                    weather_data: dict = current_weather.model_dump(
                        exclude={"condition", "air_quality"}
                    )
                    condition_data: dict = current_weather.condition.model_dump()
                    air_qual_data: dict = (
                        current_weather.air_quality.model_dump()
                        if current_weather.air_quality
                        else {}
                    )

                    ## Set location of current weather reading
                    weather_data["location_id"] = db_location.id

                    log.debug(f"Save current weather")
                    try:
                        db_current_weather: CurrentWeatherModel = (
                            current_weather_repository.create_with_related(
                                weather_data=weather_data,
                                condition_data=condition_data,
                                air_quality_data=air_qual_data,
                            )
                        )
                    except Exception as exc:
                        log.error(f"Error saving current weather: {exc}")
                        raise HTTPException(
                            status_code=400, detail="Error saving current weather"
                        )

                case _:
                    log.error(f"Invalid label: {payload.label}")
                    raise HTTPException(status_code=400, detail="Invalid label")

        case _:
            log.error(f"Invalid source: {payload.source}")
            raise HTTPException(status_code=400, detail="Invalid source")

    return {
        "weather_id": db_current_weather.id,
        "message": "Current weather data saved successfully",
    }
