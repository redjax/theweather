from __future__ import annotations

import typing as t

from weatherapi_collector import (
    client as weatherapi_client,
    db_client,
)
from weatherapi_collector.depends import get_db_engine

from loguru import logger as log
from shared.domain.weatherapi.weather import (
    CurrentWeatherJSONIn,
    CurrentWeatherJSONModel,
    ForecastJSONIn,
    ForecastJSONModel,
)
import sqlalchemy as sa

__all__ = ["job_weatherapi_current_weather", "job_weatherapi_weather_forecast"]


def job_weatherapi_current_weather(
    location_name: str,
    api_key: str,
    save_to_db: bool = False,
    db_echo: bool = False,
    engine: t.Optional[sa.Engine] = None,
):
    log.info(
        f"[Scheduled Job] Collect current weather for location '{location_name}' from WeatherAPI"
    )
    if save_to_db:
        engine = get_db_engine()

    try:
        result = weatherapi_client.get_current_weather(
            location=location_name,
            api_key=api_key,
        )
        log.info(f"Collected current weather for location '{location_name}'")
    except Exception as exc:
        log.error(
            f"({type(exc)}) Error running scheduled job to collect current weather for location '{location_name}' from WeatherAPI: {exc}"
        )
        raise

    if save_to_db:
        log.info(f"Saving current weather response to the database")
        try:
            db_client.save_current_weather_response(
                current_weather_schema=CurrentWeatherJSONIn(
                    current_weather_json=result
                ),
                echo=db_echo,
            )
        except Exception as exc:
            log.error(
                f"({type(exc)}) Error saving current weather response JSON to the database: {exc}"
            )
            raise


def job_weatherapi_weather_forecast(
    location_name: str,
    api_key: str,
    forecast_days: int = 1,
    save_to_db: bool = False,
    db_echo: bool = False,
    engine: t.Optional[sa.Engine] = None,
):
    log.info(
        f"[Scheduled Job] Collect weather forecast for location '{location_name}' from WeatherAPI"
    )

    try:
        result = weatherapi_client.get_weather_forecast(
            location=location_name,
            api_key=api_key,
            days=forecast_days,
        )
        log.info(f"Collected weather forecast for location '{location_name}'")
    except Exception as exc:
        log.error(
            f"({type(exc)}) Error running scheduled job to collect weather forecast for location '{location_name}' from WeatherAPI: {exc}"
        )

    if save_to_db:
        log.info(f"Saving current weather response to the database")
        try:
            db_client.save_forecast(
                forecast_schema=ForecastJSONIn(forecast_json=result),
                echo=db_echo,
            )
        except Exception as exc:
            log.error(f"Failed saving forecast response JSON to database: {exc}")
            raise
