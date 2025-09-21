import time

from shared.config import SHARED_SETTINGS
from shared.http_lib.config import HTTP_SETTINGS
from shared import http_lib
from shared.depends import get_httpx_controller
from shared.setup import setup_loguru_logging

from weatherapi_collector.config import WEATHERAPI_SETTINGS
from weatherapi_collector import client as weatherapi_client
from weatherapi_collector.scheduled import start_weatherapi_scheduled_collection

import schedule
from loguru import logger as log


def collect_current_weather(location_name: str | None = None) -> dict:
    return weatherapi_client.get_current_weather(location=location_name)


def collect_weather_forecast(locatin_name: str | None = None, days: int = 1) -> dict:
    return weatherapi_client.get_weather_forecast(location=locatin_name, days=days)


def collect(location_name: str | None = None, forecast_days: int = 1) -> dict:
    ## Current weather
    try:
        current_weather: dict = collect_current_weather(location_name)
        log.debug(f"Current weather in '{location_name}': {current_weather}")
    except Exception as exc:
        log.error(
            f"({type(exc)} Failed to request current weather for location '{location_name}': {exc}"
        )
        raise

    ## Weather forecast
    try:
        weather_forecast: dict = collect_weather_forecast(
            location_name, days=forecast_days
        )
        log.debug(f"Weather forecast for '{location_name}': {weather_forecast}")
    except Exception as exc:
        log.error(
            f"({type(exc)}) Failed to request weather forecast for location '{location_name}': {exc}"
        )
        raise

    return {"current_weather": current_weather, "weather_forecast": weather_forecast}


def main(start_scheduled: bool = False):
    location_name: str = WEATHERAPI_SETTINGS.get("LOCATION_NAME")
    forecast_days: int = 1

    if start_scheduled:
        start_weatherapi_scheduled_collection(
            location_name=location_name,
            api_key=WEATHERAPI_SETTINGS.get("API_KEY"),
            forecast_days=forecast_days,
        )

    else:
        log.info(f"Running collector for location '{location_name}'")
        try:
            collected_weatherapi_results: dict = collect(location_name, forecast_days)
        except KeyboardInterrupt:
            log.warning("Execution cancelled by user (CTRL+C).")
            return


if __name__ == "__main__":
    setup_loguru_logging()

    RUN_SCHEDULE: bool = True

    try:
        main(start_scheduled=RUN_SCHEDULE)
    except Exception as exc:
        log.error(f"({type(exc)}) Failed to run WeatherAPI collector: {exc}")
        exit(1)
