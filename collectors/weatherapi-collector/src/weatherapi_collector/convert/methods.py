from __future__ import annotations

import json
import typing as t

from loguru import logger as log
from shared.domain.weatherapi.location import (
    LocationIn,
    LocationModel,
    LocationOut,
)
from shared.domain.weatherapi.weather.current import (
    CurrentWeatherIn,
    CurrentWeatherJSONIn,
    CurrentWeatherJSONModel,
    CurrentWeatherJSONOut,
    CurrentWeatherModel,
    CurrentWeatherOut,
)
from shared.domain.weatherapi.weather.forecast import (
    ForecastJSONIn,
    ForecastJSONModel,
    ForecastJSONOut,
    ForecastJSONRepository,
)

__all__ = [
    "current_weather_dict_to_schema",
    "current_weather_response_dict_to_schema",
    "location_dict_to_schema",
    "current_weather_schema_to_model",
    "weather_forecast_dict_to_schema",
    "current_weather_api_response_to_dict",
    "current_weather_api_response_dict_to_schemas",
    "location_schema_to_model",
]


@log.catch
def current_weather_dict_to_schema(current_weather_dict: dict):
    """Convert a current weather dictionary to a CurrentWeatherIn schema.

    Params:
        current_weather_dict (dict): The current weather dictionary to convert.

    Returns:
        CurrentWeatherIn: The converted CurrentWeatherIn schema.

    """
    current_weather: CurrentWeatherIn = CurrentWeatherIn.model_validate(
        current_weather_dict
    )

    return current_weather


@log.catch
def location_dict_to_schema(location_dict: dict):
    """Convert a location dictionary to a LocationIn schema.

    Params:
        location_dict (dict): The location dictionary to convert.

    Returns:
        LocationIn: The converted LocationIn schema.

    """
    location: LocationIn = LocationIn.model_validate(location_dict)

    return location


@log.catch
def location_schema_to_model(location_schema: LocationIn) -> LocationModel:
    """Convert a location schema to a database model.

    Params:
        location_schema (LocationIn): The location schema to convert.

    Returns:
        LocationModel: The converted database model.

    """
    location_model: LocationModel = LocationModel(**location_schema.model_dump())

    return location_model


@log.catch
def current_weather_schema_to_model(
    current_weather_schema: CurrentWeatherIn, location_schema: LocationIn
) -> CurrentWeatherModel:
    """Convert a current weather schema to a database model.

    Params:
        current_weather_schema (CurrentWeatherIn): The current weather schema to convert.

    Returns:
        CurrentWeatherModel: The converted database model.

    """
    raise NotImplementedError(
        "Converting current weather schema to model not yet implemented"
    )

    current_weather_dict: dict = current_weather_schema.model_dump()
    current_weather_condition_dict: dict = current_weather_schema.condition.model_dump()
    current_weather_air_quality_dict: dict = (
        current_weather_schema.air_quality.model_dump()
    )

    model_dict = {
        "last_updated_epoch": current_weather_dict["last_updated_epoch"],
        "last_updated": current_weather_dict["last_updated"],
        "temp_c": current_weather_dict["temp_c"],
        "temp_f": current_weather_dict["temp_f"],
        "condition": current_weather_condition_dict,
        "air_quality": current_weather_air_quality_dict,
        "is_day": current_weather_dict["is_day"],
        "wind_mph": current_weather_dict["wind_mph"],
        "wind_kph": current_weather_dict["wind_kph"],
        "wind_degree": current_weather_dict["wind_degree"],
        "wind_dir": current_weather_dict["wind_dir"],
        "pressure_mb": current_weather_dict["pressure_mb"],
        "pressure_in": current_weather_dict["pressure_in"],
        "precip_mm": current_weather_dict["precip_mm"],
        "precip_in": current_weather_dict["precip_in"],
        "humidity": current_weather_dict["humidity"],
        "cloud": current_weather_dict["cloud"],
        "feelslike_c": current_weather_dict["feelslike_c"],
        "feelslike_f": current_weather_dict["feelslike_f"],
        "windchill_c": current_weather_dict["windchill_c"],
        "windchill_f": current_weather_dict["windchill_f"],
        "heatindex_c": current_weather_dict["heatindex_c"],
        "heatindex_f": current_weather_dict["heatindex_f"],
        "dewpoint_c": current_weather_dict["dewpoint_c"],
        "dewpoint_f": current_weather_dict["dewpoint_f"],
        "vis_km": current_weather_dict["vis_km"],
        "uv": current_weather_dict["uv"],
        "gust_mph": current_weather_dict["gust_mph"],
        "gust_kph": current_weather_dict["gust_kph"],
    }

    try:
        current_weather_model: CurrentWeatherModel = CurrentWeatherModel(**model_dict)

        return current_weather_model
    except Exception as exc:
        msg = f"({type(exc)}) Error converting current weather schema to model. Details: {exc}"
        log.error(msg)

        raise


@log.catch
def weather_forecast_dict_to_schema(weather_forecast_dict: dict) -> ForecastJSONIn:
    """Convert a weather forecast dictionary to a ForecastJSONIn schema.

    Params:
        weather_forecast_dict (dict): The weather forecast dictionary to convert.

    Returns:
        ForecastJSONIn: The converted ForecastJSONIn schema.

    """
    weather_forecast_json: ForecastJSONIn = ForecastJSONIn(
        forecast_json=weather_forecast_dict
    )

    return weather_forecast_json


@log.catch
def current_weather_response_dict_to_schema(
    current_weather_response_dict: dict,
) -> CurrentWeatherJSONIn:
    """Convert a current weatheer response dictionary to a CurrentWeatherJSONIn schema.

    Params:
      current_weather_response_dict (dict): The raw current weather response dictionary to convert.

    Returns:
      CurrentWeatherJSONIn: The converted CurrentWeatherJSONIn schema.

    """
    current_weather_json: CurrentWeatherJSONIn = CurrentWeatherJSONIn(
        current_weather_json=current_weather_response_dict
    )

    return current_weather_json


@log.catch
def current_weather_api_response_to_dict(content: t.Union[dict, str, bytes]):
    """Convert a current weather API response to a dictionary.

    Params:
        content (dict | str | bytes): The current weather API response to convert.

    Returns:
        dict: The converted dictionary.

    """
    if content is None:
        raise ValueError("Missing response content to convert")
    if isinstance(content, str):
        log.debug("Decoding response content string")
        content: dict = json.load(content)
    if isinstance(content, bytes):
        log.debug(f"Decoding content bytestring")
        content_str: str = content.decode("utf-8")
        content: dict = json.load(content_str)
    if isinstance(content, dict):
        return content

    return content


@log.catch
def current_weather_api_response_dict_to_schemas(
    content_dict: dict,
) -> list[dict[str, t.Union[LocationIn, CurrentWeatherIn]]]:
    """Convert a current weather API response dictionary to a list of LocationIn and CurrentWeatherIn schemas.

    Params:
        content_dict (dict): The current weather API response dictionary to convert.

    Returns:
        list[dict[str, t.Union[LocationIn, CurrentWeatherIn]]]: The converted list of LocationIn and CurrentWeatherIn schemas.

    """
    if not content_dict:
        raise ValueError("Missing a content dict to decode into objects")
    if not isinstance(content_dict, dict):
        raise TypeError(
            f"Invalid type for content_dict: {type(content_dict)}. Must be a dict."
        )

    current_weather_dict: dict = content_dict["current"]
    location_dict: dict = content_dict["location"]

    return_obj: dict[str, t.Union[LocationIn, CurrentWeatherIn]] = {
        "location": None,
        "current_weather": None,
    }

    try:
        current_weather: CurrentWeatherIn = current_weather_dict_to_schema(
            current_weather_dict
        )
        return_obj["current_weather"] = current_weather
    except Exception as exc:
        msg = f"({type(exc)}) Error converting current weather dict to CurrentWeatherIn schema. Details: {exc}"
        log.error(msg)

    try:
        location: LocationIn = location_dict_to_schema(location_dict)
        return_obj["location"] = location
    except Exception as exc:
        msg = f"({type(exc)}) Error converting location dict to LocationIn schema.  Details: {exc}"

    return return_obj
