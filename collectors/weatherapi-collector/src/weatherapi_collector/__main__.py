from shared.setup import setup_loguru_logging
from shared.domain.weatherapi.weather import CurrentWeatherJSONIn, ForecastJSONIn

from weatherapi_collector.config import WEATHERAPI_SETTINGS
from weatherapi_collector import client as weatherapi_client
from weatherapi_collector.scheduled import start_weatherapi_scheduled_collection
from weatherapi_collector import db_client
from weatherapi_collector.depends import get_db_engine
from weatherapi_collector.db_init import initialize_database

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


def main(start_scheduled: bool = False, save_to_db: bool = False):
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

            if save_to_db:
                _current = CurrentWeatherJSONIn(
                    collected_weatherapi_results.get("current_weather")
                )
                _forecast = ForecastJSONIn(
                    collected_weatherapi_results.get("weather_forecast")
                )

                engine = get_db_engine()

                log.info(f"Saving WeatherAPI HTTP responses to DB")

                log.debug(f"Saving current weather to DB")
                try:
                    db_client.save_current_weather_response(
                        current_weather_schema=_current, engine=engine
                    )
                except Exception as exc:
                    log.error(f"Failed to save current weather to DB: {exc}")
                    raise

                log.debug(f"Saving forecast to DB")
                try:
                    db_client.save_forecast_response(
                        forecast_schema=_forecast, engine=engine
                    )
                except Exception as exc:
                    log.error(f"Failed to save forecast to DB: {exc}")
                    raise

        except KeyboardInterrupt:
            log.warning("Execution cancelled by user (CTRL+C).")
            return


if __name__ == "__main__":
    setup_loguru_logging()

    RUN_SCHEDULE: bool = WEATHERAPI_SETTINGS.get("RUN_SCHEDULER", False)
    SAVE_TO_DB: bool = WEATHERAPI_SETTINGS.get("SAVE_TO_DB", False)
    log.debug(f"Running on schedule: {RUN_SCHEDULE}")
    log.debug(f"Save responses to DB: {SAVE_TO_DB}")

    initialize_database()

    try:
        main(start_scheduled=RUN_SCHEDULE, save_to_db=SAVE_TO_DB)
    except Exception as exc:
        log.error(f"({type(exc)}) Failed to run WeatherAPI collector: {exc}")
        exit(1)
