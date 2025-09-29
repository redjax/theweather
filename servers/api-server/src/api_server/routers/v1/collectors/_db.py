import typing as t

from shared.domain.weatherapi.location import (
    LocationIn,
    LocationModel,
    LocationRepository,
)
from shared.domain.weatherapi.weather import (
    CurrentWeatherIn,
    CurrentWeatherModel,
    CurrentWeatherRepository,
    CurrentWeatherJSONModel,
    CurrentWeatherJSONIn,
    CurrentWeatherJSONRepository,
    ForecastJSONModel,
    ForecastJSONIn,
    ForecastJSONOut,
    ForecastJSONRepository,
)

from loguru import logger as log
from sqlalchemy.orm import Session

__all__ = ["save_weatherapi_current_weather"]


def save_weatherapi_current_weather(
    data: dict, session: Session
) -> dict[str, t.Union[LocationModel, CurrentWeatherModel, CurrentWeatherJSONModel]]:
    """Save WeatherAPI collector payload data to database.

    Params:
        data (dict): JSON payload data (WeatherAPI response) from collector.
        session (Session): SQLAlchemy database session.

    Returns:
        dict[str, t.Union[LocationModel, CurrentWeatherModel, CurrentWeatherJSONModel]]: Dictionary of models from database.
    """
    ## Raw JSON response schema
    raw_json = CurrentWeatherJSONIn(current_weather_json=data)
    log.debug(f"Raw JSON: {raw_json}")

    _data = data["current_weather_json"]

    ## Location schema
    location = LocationIn.model_validate(_data["location"])
    ## Current weather schema
    current_weather = CurrentWeatherIn.model_validate(_data["current"])

    ## Build DB models
    location_model: LocationModel = LocationModel(**location.model_dump())
    current_weather_model = current_weather.to_orm()

    ## Initialize repositories
    current_weather_json_repo = CurrentWeatherJSONRepository(session)
    location_repo = LocationRepository(session)
    current_weather_repo = CurrentWeatherRepository(session)

    ## Save raw JSON
    log.debug("Saving raw current weather JSON")
    try:
        db_current_weather_json = current_weather_json_repo.create(
            current_weather_json_model := CurrentWeatherJSONModel(
                current_weather_json=raw_json.current_weather_json
            )
        )
        log.debug("Saved raw current weather JSON")
    except Exception as exc:
        log.error(f"Unhandled exception saving current weather JSON: {exc}")
        raise

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
        raise

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
        weather_data = current_weather.model_dump(exclude={"condition", "air_quality"})
        weather_data["location_id"] = db_location.id
        condition_data = current_weather.condition.model_dump()
        air_qual_data = (
            current_weather.air_quality.model_dump()
            if current_weather.air_quality
            else {}
        )

        try:
            db_current_weather = current_weather_repo.create_with_related(
                weather_data=weather_data,
                condition_data=condition_data,
                air_quality_data=air_qual_data,
            )
            log.debug(f"Saved current weather with id {db_current_weather.id}")
        except Exception as exc:
            log.error(f"Error saving current weather: {exc}")
            raise

    return {
        "current_weather": db_current_weather,
        "current_weather_json": db_current_weather_json,
        "location": db_location,
    }


def save_weatherapi_weather_forecast(
    data: dict, session: Session
) -> dict[str, t.Union[LocationModel, ForecastJSONModel]]:
    """Save WeatherAPI forecast collector payload data to database.

    Params:
        data (dict): JSON payload data (WeatherAPI response) from collector.
        session (Session): SQLAlchemy database session.

    Returns:
        dict[str, t.Union[LocationModel, ForecastJSONModel]]: Dictionary of models from database.
    """
    ## Raw JSON response schema
    raw_json = ForecastJSONIn(forecast_json=data)
    log.debug(f"Raw JSON: {raw_json}")

    _data = data["forecast_json"]

    ## Location schema
    location = LocationIn.model_validate(_data["location"])

    ## Build DB models
    location_model: LocationModel = LocationModel(**location.model_dump())

    ## Initialize repositories
    forecast_json_repo = ForecastJSONRepository(session)
    location_repo = LocationRepository(session)

    ## Save raw JSON
    log.debug("Saving raw forecast weather JSON")
    try:
        db_forecast_json = forecast_json_repo.create(
            forecast_json_model := ForecastJSONModel(
                forecast_json=raw_json.forecast_json
            )
        )
        log.debug("Saved raw forecast weather JSON")
    except Exception as exc:
        log.error(f"Unhandled exception saving forecast weather JSON: {exc}")
        raise

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
        raise

    return {
        "forecast_json": db_forecast_json,
        "location": db_location,
    }
