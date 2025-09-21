import time

from weatherapi_collector import client as weatherapi_client

import schedule
from loguru import logger as log

__all__ = ["start_weatherapi_scheduled_collection", "add_weatherapi_schedules"]


def job_weatherapi_current_weather(location_name: str, api_key: str):
    log.info(
        f"[Scheduled Job] Collect current weather for location '{location_name}' from WeatherAPI"
    )
    try:
        result = weatherapi_client.get_current_weather(
            location=location_name, api_key=api_key
        )
        log.info(f"Collected current weather for location '{location_name}'")
    except Exception as exc:
        log.error(
            f"({type(exc)}) Error running scheduled job to collect current weather for location '{location_name}' from WeatherAPI: {exc}"
        )
        raise


def job_weatherapi_weather_forecast(
    location_name: str, api_key: str, forecast_days: int = 1
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


def add_weatherapi_schedules(
    location_name: str,
    api_key: str,
    forecast_days: int = 1,
):
    for minute in ["00", "15", "30", "45"]:
        ## Current weather
        schedule.every().hour.at(f":{minute}").do(
            job_weatherapi_current_weather, location_name=location_name, api_key=api_key
        )

        ## Weather forecast
        schedule.every().hour.at(f":{minute}").do(
            job_weatherapi_weather_forecast,
            location_name=location_name,
            api_key=api_key,
            forecast_days=forecast_days,
        )


def start_weatherapi_scheduled_collection(
    location_name: str,
    api_key: str,
    forecast_days: int = 1,
):
    add_weatherapi_schedules(
        location_name=location_name,
        api_key=api_key,
        forecast_days=forecast_days,
    )

    log.info(f"Starting scheduler loop [interval: HH:00, HH:15, HH:30, HH:45]")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        log.warning("Execution cancelled by user (CTRL+C).")
    except Exception as exc:
        log.error(f"Failed to run scheduled collection loop: {exc}")
        raise
