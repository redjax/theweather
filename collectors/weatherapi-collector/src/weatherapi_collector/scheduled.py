import time
import typing as t

from shared.domain.weatherapi.weather import (
    ForecastJSONModel,
    ForecastJSONIn,
    CurrentWeatherJSONModel,
    CurrentWeatherJSONIn,
)
from weatherapi_collector.depends import get_db_engine
from weatherapi_collector import db_client
from weatherapi_collector import client as weatherapi_client

import sqlalchemy as sa

import schedule
from loguru import logger as log

__all__ = ["start_weatherapi_scheduled_collection", "add_weatherapi_schedules"]


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
    engine = None
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
                engine=engine,
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
                engine=engine,
                echo=db_echo,
            )
        except Exception as exc:
            log.error(f"Failed saving forecast response JSON to database: {exc}")
            raise


def add_weatherapi_schedules(
    location_name: str,
    api_key: str,
    forecast_days: int = 1,
    minutes_schedule: list[str] = ["00", "15", "30", "45"],
    save_to_db: bool = False,
    db_echo: bool = False,
    db_engine: t.Optional[sa.Engine] = None,
):
    for minute in minutes_schedule:
        ## Current weather
        schedule.every().hour.at(f":{minute}").do(
            job_weatherapi_current_weather,
            location_name=location_name,
            api_key=api_key,
            save_to_db=save_to_db,
            db_echo=db_echo,
            engine=db_engine,
        )

        ## Weather forecast
        schedule.every().hour.at(f":{minute}").do(
            job_weatherapi_weather_forecast,
            location_name=location_name,
            api_key=api_key,
            forecast_days=forecast_days,
            save_to_db=save_to_db,
            db_echo=db_echo,
            engine=db_engine,
        )


def start_weatherapi_scheduled_collection(
    location_name: str,
    api_key: str,
    forecast_days: int = 1,
    save_to_db: bool = False,
    db_echo: bool = False,
    minutes_schedule: list[str] = ["00", "15", "30", "45"],
    db_engine: t.Optional[sa.Engine] = None,
):
    add_weatherapi_schedules(
        location_name=location_name,
        api_key=api_key,
        forecast_days=forecast_days,
        save_to_db=save_to_db,
        db_echo=db_echo,
        db_engine=db_engine,
        minutes_schedule=minutes_schedule,
    )

    log.info(
        f"Starting scheduler loop (minutes where schedule will run: {minutes_schedule})"
    )
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        log.warning("Execution cancelled by user (CTRL+C).")
    except Exception as exc:
        log.error(f"Failed to run scheduled collection loop: {exc}")
        raise
