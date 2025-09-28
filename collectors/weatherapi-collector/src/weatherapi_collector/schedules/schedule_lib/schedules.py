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

from .jobs import (
    job_weatherapi_current_weather,
    job_weatherapi_weather_forecast,
    job_post_weather_readings,
)

import sqlalchemy as sa

import schedule
from loguru import logger as log


__all__ = ["start_weatherapi_scheduled_collection", "add_weatherapi_schedules"]


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


def add_data_schedules(
    db_echo: bool = False,
    minutes_schedule: list[str] = ["00", "15", "30", "45"],
):
    for minute in minutes_schedule:
        schedule.every().hour.at(f":{minute}").do(
            job_post_weather_readings, echo=db_echo
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

    add_data_schedules(
        db_echo=db_echo,
        minutes_schedule=[
            "00",
            "05",
            "10",
            "15",
            "20",
            "25",
            "30",
            "35",
            "40",
            "45",
            "50",
            "55",
        ],
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
