from shared.domain.collectors.payloads import WeatherCollectorPayloadIn
from shared.domain.weatherapi.weather import (
    CurrentWeatherJSONIn,
    CurrentWeatherJSONModel,
    CurrentWeatherJSONRepository,
    CurrentWeatherIn,
    CurrentWeatherModel,
    CurrentWeatherRepository,
)
from shared.domain.weatherapi.location import (
    LocationIn,
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
        case "weatherapi":
            match payload.label:
                case "current":
                    log.info(f"Received current weather from collector")

                    ## Raw JSON response schema
                    raw_json = CurrentWeatherJSONIn(current_weather_json=payload.data)

                    ## Location schema
                    location = LocationIn.model_validate(payload.data["location"])
                    ## Current weather schema
                    current_weather = CurrentWeatherIn.model_validate(
                        payload.data["current"]
                    )

                    ## Build DB models
                    location_model = LocationModel(**location.model_dump())
                    current_weather_model = current_weather.to_orm()

                    ## Initialize repositories
                    current_weather_json_repo = CurrentWeatherJSONRepository(db)
                    location_repo = LocationRepository(db)
                    current_weather_repo = CurrentWeatherRepository(db)

                    ## Save raw JSON
                    try:
                        db_current_weather_json = current_weather_json_repo.create(
                            current_weather_json_model := CurrentWeatherJSONModel(
                                current_weather_json=raw_json.current_weather_json
                            )
                        )
                        log.debug("Saved raw current weather JSON")
                    except Exception as exc:
                        log.error(f"Error saving current weather JSON: {exc}")
                        raise HTTPException(
                            status_code=400, detail="Error saving current weather JSON"
                        )

                    ## Check if Location exists, else save
                    try:
                        db_location = location_repo.get_by_name_country_and_region(
                            location_model.name,
                            location_model.region,
                            location_model.country,
                        )
                        if not db_location:
                            db_location = location_repo.save(location_model)
                        log.debug(f"Using location id: {db_location.id}")
                    except Exception as exc:
                        log.error(f"Error saving location: {exc}")
                        raise HTTPException(
                            status_code=400, detail="Error saving location"
                        )

                    ## Check if current weather already exists for last_updated_epoch, skip insert if so
                    existing_weather = current_weather_repo.get_by_last_updated_epoch(
                        current_weather.last_updated_epoch
                    )
                    if existing_weather:
                        log.info(
                            f"Current weather with last_updated_epoch {current_weather.last_updated_epoch} already exists, skipping insert"
                        )
                        db_current_weather = existing_weather
                    else:
                        ## Set the location_id in weather_data dict
                        weather_data = current_weather.model_dump(
                            exclude={"condition", "air_quality"}
                        )
                        weather_data["location_id"] = db_location.id
                        condition_data = current_weather.condition.model_dump()
                        air_qual_data = (
                            current_weather.air_quality.model_dump()
                            if current_weather.air_quality
                            else {}
                        )

                        try:
                            db_current_weather = (
                                current_weather_repo.create_with_related(
                                    weather_data=weather_data,
                                    condition_data=condition_data,
                                    air_quality_data=air_qual_data,
                                )
                            )
                            log.debug(
                                f"Saved current weather with id {db_current_weather.id}"
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
