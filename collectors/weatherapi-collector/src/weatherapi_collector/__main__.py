from __future__ import annotations

from copy import deepcopy
import typing as t

from weatherapi_collector import (
    client as weatherapi_client,
    db_client,
)
from weatherapi_collector.config import WEATHERAPI_SETTINGS
from weatherapi_collector.db_init import initialize_database
from weatherapi_collector.depends import get_db_engine
from weatherapi_collector.schedules.apscheduler_lib import (
    default_cron_schedule,
    start_scheduler,
)
from weatherapi_collector.schedules.schedule_lib import (
    start_weatherapi_scheduled_collection,
)

from loguru import logger as log
from shared.domain.weatherapi.weather import CurrentWeatherJSONIn, ForecastJSONIn
from shared.setup import setup_loguru_logging
import sqlalchemy as sa


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


def start_schedule_lib_schedules(
    run_schedule: bool = False,
    save_to_db: bool = False,
    db_echo: bool = False,
    weatherapi_jobs_schedule_minutes_list: list[str] = [],
    data_jobs_minutes_schedule: list[str] = [],
    cleanup_jobs_minutes_schedule: list[str] = [],
):

    ## Initialize database engine
    db_engine = None
    if save_to_db:
        db_engine = get_db_engine()

    log.debug(
        f"Start scheduler: {run_schedule}, save to DB: {save_to_db}, DB echo: {db_echo}"
    )
    location_name: str = WEATHERAPI_SETTINGS.get("LOCATION_NAME")
    forecast_days: int = 1

    if run_schedule:
        start_weatherapi_scheduled_collection(
            location_name=location_name,
            api_key=WEATHERAPI_SETTINGS.get("API_KEY"),
            forecast_days=forecast_days,
            save_to_db=save_to_db,
            db_echo=db_echo,
            weatherapi_jobs_minutes_schedule=weatherapi_jobs_schedule_minutes_list,
            data_jobs_minutes_schedule=data_jobs_minutes_schedule,
            cleanup_jobs_minutes_schedule=cleanup_jobs_minutes_schedule,
            db_engine=db_engine,
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
                    db_client.save_forecast(forecast_schema=_forecast, engine=engine)
                except Exception as exc:
                    log.error(f"Failed to save forecast to DB: {exc}")
                    raise

        except KeyboardInterrupt:
            log.warning("Execution cancelled by user (CTRL+C).")
            return


def start_apscheduler_lib_schedules(
    run_schedule: bool = False,
    schedules_dict: dict[str, dict[str, t.Any]] | None = None,
    db_echo: bool = False,
    save_to_db: bool = False,
):
    location_name: str = WEATHERAPI_SETTINGS.get("LOCATION_NAME")
    forecast_days: int = 1

    if run_schedule:
        start_scheduler(
            schedules_dict=schedules_dict or {},
            location_name=location_name,
            api_key=WEATHERAPI_SETTINGS.get("API_KEY"),
            forecast_days=forecast_days,
            save_to_db=save_to_db,
            db_echo=db_echo,
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
                    db_client.save_forecast(forecast_schema=_forecast, engine=engine)
                except Exception as exc:
                    log.error(f"Failed to save forecast to DB: {exc}")
                    raise

        except KeyboardInterrupt:
            log.warning("Execution cancelled by user (CTRL+C).")
            return


def main():

    _MANUAL_HTTP_MINUTES = []
    _MANUAL_DATA_MINUTES = []
    _MANUAL_CLEANUP_MINUTES = []

    RUN_SCHEDULE: bool = WEATHERAPI_SETTINGS.get("RUN_SCHEDULER")
    SCHEDULER: str = WEATHERAPI_SETTINGS.get("SCHEDULER")
    SAVE_TO_DB: bool = WEATHERAPI_SETTINGS.get("SAVE_TO_DB")
    DB_ECHO: bool = WEATHERAPI_SETTINGS.get("DB_ECHO")
    log.debug(f"Running on schedule: {RUN_SCHEDULE}")
    log.debug(f"Save responses to DB: {SAVE_TO_DB}, DB echo: {DB_ECHO}")

    if RUN_SCHEDULE and SCHEDULER not in ["schedule_lib", "apscheduler_lib"]:
        log.error(f"Invalid scheduler '{SCHEDULER}' for running on schedule")
        raise ValueError(f"Invalid scheduler '{SCHEDULER}' for running on schedule")

    initialize_database()

    ####################
    # Schedule library #
    ####################

    SCHEDULE_LIB_WEATHERAPI_JOBS_SCHEDULE_MINUTES_LIST = ["00", "15", "30", "45"]
    SCHEDULE_LIB_DATA_JOBS_SCHEDULE_MINUTES_LIST: list[str] = ["00", "20", "40"]
    SCHEDULE_LIB_CLEANUP_JOBS_SCHEDULE_MINUTES_LIST: list[str] = [
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
    ]

    ## Override schedules (for debugging/dev)
    SCHEDULE_LIB_OVERRIDES = {
        "SCHEDULE_LIB_WEATHERAPI_JOBS_SCHEDULE_MINUTES_LIST": [] + _MANUAL_HTTP_MINUTES,
        "SCHEDULE_LIB_DATA_JOBS_SCHEDULE_MINUTES_LIST": [] + _MANUAL_DATA_MINUTES,
        "SCHEDULE_LIB_CLEANUP_JOBS_SCHEDULE_MINUTES_LIST": [] + _MANUAL_CLEANUP_MINUTES,
    }

    ## Override weather api jobs schedule
    if SCHEDULE_LIB_OVERRIDES.get("SCHEDULE_LIB_WEATHERAPI_JOBS_SCHEDULE_MINUTES_LIST"):
        SCHEDULE_LIB_WEATHERAPI_JOBS_SCHEDULE_MINUTES_LIST = (
            SCHEDULE_LIB_WEATHERAPI_JOBS_SCHEDULE_MINUTES_LIST
            + SCHEDULE_LIB_OVERRIDES.get(
                "SCHEDULE_LIB_WEATHERAPI_JOBS_SCHEDULE_MINUTES_LIST"
            )
        )

    ## Override data jobs schedule
    if SCHEDULE_LIB_OVERRIDES.get("SCHEDULE_LIB_DATA_JOBS_SCHEDULE_MINUTES_LIST"):
        SCHEDULE_LIB_DATA_JOBS_SCHEDULE_MINUTES_LIST = (
            SCHEDULE_LIB_DATA_JOBS_SCHEDULE_MINUTES_LIST
            + SCHEDULE_LIB_OVERRIDES.get("SCHEDULE_LIB_DATA_JOBS_SCHEDULE_MINUTES_LIST")
        )

    ## Override cleanup jobs schedule
    if SCHEDULE_LIB_OVERRIDES.get("SCHEDULE_LIB_CLEANUP_JOBS_SCHEDULE_MINUTES_LIST"):
        SCHEDULE_LIB_CLEANUP_JOBS_SCHEDULE_MINUTES_LIST = (
            SCHEDULE_LIB_CLEANUP_JOBS_SCHEDULE_MINUTES_LIST
            + SCHEDULE_LIB_OVERRIDES.get(
                "SCHEDULE_LIB_CLEANUP_JOBS_SCHEDULE_MINUTES_LIST"
            )
        )

    #######################
    # APScheduler library #
    #######################

    ## Set weatherapi job schedule for APScheduler from schedule lib settings
    APSCHEDULER_LIB_WEATHERAPI_JOBS_SCHEDULE_CRON = deepcopy(default_cron_schedule)
    APSCHEDULER_LIB_WEATHERAPI_JOBS_SCHEDULE_CRON["minute"] = ",".join(
        SCHEDULE_LIB_WEATHERAPI_JOBS_SCHEDULE_MINUTES_LIST
    )

    ## Set data jobs schedule for APScheduler from schedule lib settings
    APSCHEDULER_LIB_DATA_JOBS_SCHEDULE_CRON = deepcopy(default_cron_schedule)
    APSCHEDULER_LIB_DATA_JOBS_SCHEDULE_CRON["minute"] = ",".join(
        SCHEDULE_LIB_DATA_JOBS_SCHEDULE_MINUTES_LIST
    )

    ## Set cleanup jobs schedule for APScheduler from schedule lib settings
    APSCHEDULER_LIB_CLEANUP_JOBS_SCHEDULE_CRON = deepcopy(default_cron_schedule)
    APSCHEDULER_LIB_CLEANUP_JOBS_SCHEDULE_CRON["minute"] = ",".join(
        SCHEDULE_LIB_CLEANUP_JOBS_SCHEDULE_MINUTES_LIST
    )

    ## All APScheduler jobs schedules
    APSCHEDULER_LIB_JOBS_SCHEDULES = {
        "weatherapi_jobs": APSCHEDULER_LIB_WEATHERAPI_JOBS_SCHEDULE_CRON,
        "data_jobs": APSCHEDULER_LIB_DATA_JOBS_SCHEDULE_CRON,
        "cleanup_jobs": APSCHEDULER_LIB_CLEANUP_JOBS_SCHEDULE_CRON,
    }

    ############################
    # Start Selected Scheduler #
    ############################

    match SCHEDULER:
        case "schedule_lib":
            start_schedule_lib_schedules(
                run_schedule=RUN_SCHEDULE,
                save_to_db=SAVE_TO_DB,
                db_echo=DB_ECHO,
                weatherapi_jobs_schedule_minutes_list=SCHEDULE_LIB_WEATHERAPI_JOBS_SCHEDULE_MINUTES_LIST,
                data_jobs_minutes_schedule=SCHEDULE_LIB_DATA_JOBS_SCHEDULE_MINUTES_LIST,
                cleanup_jobs_minutes_schedule=SCHEDULE_LIB_CLEANUP_JOBS_SCHEDULE_MINUTES_LIST,
            )
        case "apscheduler_lib":
            start_apscheduler_lib_schedules(
                run_schedule=RUN_SCHEDULE,
                schedules_dict=APSCHEDULER_LIB_JOBS_SCHEDULES,
                db_echo=DB_ECHO,
                save_to_db=SAVE_TO_DB,
            )
        case _:
            log.error(f"Unknown scheduler: {SCHEDULER}")
            raise ValueError(f"Unknown scheduler: {SCHEDULER}")


if __name__ == "__main__":
    setup_loguru_logging()

    try:
        main()
    except Exception as exc:
        log.error(f"({type(exc)}) Failed to run WeatherAPI collector: {exc}")
        exit(1)
