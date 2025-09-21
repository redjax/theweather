from __future__ import annotations

import time

# from depends import db_depends
from shared import http_lib

# from weatherapi_collector.db_client.forecast import save_forecast
from weatherapi_collector.config import WEATHERAPI_SETTINGS
from weatherapi_collector.convert import weather_forecast_dict_to_schema

from . import requests

import httpx
from loguru import logger as log
import sqlalchemy as sa

__all__ = ["get_weather_forecast"]


def get_weather_forecast(
    location: str = WEATHERAPI_SETTINGS.get("LOCATION_NAME"),
    days: int = 1,
    api_key: str = WEATHERAPI_SETTINGS.get("API_KEY"),
    include_aqi: bool = True,
    include_alerts: bool = True,
    headers: dict | None = None,
    use_cache: bool = False,
    retry: bool = True,
    max_retries: int = 3,
    retry_sleep: int = 5,
    retry_stagger: int = 3,
    save_to_db: bool = False,
    db_engine: sa.Engine | None = None,
    db_echo: bool = False,
):
    """Get the weather forecast for a location.

    Params:
        location (str, optional): The location to get the weather forecast for. Defaults to location_name.
        days (int, optional): The number of days to get the weather forecast for. Defaults to 1.
        api_key (str, optional): The API key to use. Defaults to api_key.
        include_aqi (bool, optional): Whether to include the air quality index. Defaults to True.
        include_alerts (bool, optional): Whether to include the alerts. Defaults to True.
        headers (dict | None, optional): The headers to use. Defaults to None.
        use_cache (bool, optional): Whether to use the cache. Defaults to False.
        retry (bool, optional): Whether to retry the request. Defaults to True.
        max_retries (int, optional): The maximum number of retries to make. Defaults to 3.
        retry_sleep (int, optional): The number of seconds to sleep between retries. Defaults to 5.
        retry_stagger (int, optional): The number of seconds to stagger the retries. Defaults to 3.
        save_to_db (bool, optional): Whether to save the forecast to the database. Defaults to False.
        db_engine (Engine | None, optional): The database engine to use. If None, the default engine is used. Defaults to None.
        db_echo (bool, optional): Whether to echo SQL statements to the console. Defaults to False.

    Returns:
        dict: The weather forecast for the location.

    Raises:
        Exception: If there is an error getting the weather forecast, an `Exception` is raised.

    """
    if days > 10:
        log.warning(
            f"WeatherAPI only allows 10-day forecasts. {days} is too many, setting to 10."
        )
        days: int = 10

    weather_forecast_request: httpx.Request = requests.return_weather_forecast_request(
        days=days,
        api_key=api_key,
        location=location,
        include_aqi=include_aqi,
        headers=headers,
    )

    log.info(f"Requesting weather forecast for location: {location}")

    with http_lib.get_http_controller(use_cache=use_cache) as http:
        try:
            res: httpx.Response = http.client.send(weather_forecast_request)
        except httpx.ReadTimeout as timeout:
            log.warning(
                f"({type(timeout)}) Operation timed out while requesting weather forecast."
            )

            if not retry:
                raise timeout
            else:
                log.info(f"Retrying {max_retries} time(s)")
                current_attempt = 0
                _sleep = retry_sleep

                while current_attempt < max_retries:
                    if current_attempt > 0:
                        _sleep += retry_stagger

                    log.info(f"[Retry {current_attempt}/{max_retries}]")

                    try:
                        res: httpx.Response = http.client.send(weather_forecast_request)
                        break
                    except httpx.ReadTimeout as timeout_2:
                        log.warning(
                            f"ReadTimeout on attempt [{current_attempt}/{max_retries}]"
                        )

                        current_attempt += 1

                        time.sleep(retry_sleep)

                        continue

    log.debug(f"Response: [{res.status_code}: {res.reason_phrase}]")

    if res.status_code in http_lib.constants.SUCCESS_CODES:
        log.info("Success requesting weather forecast")
        decoded = http_lib.decode_response(response=res)
    elif res.status_code in http_lib.constants.ALL_ERROR_CODES:
        log.warning(f"Error: [{res.status_code}: {res.reason_phrase}]: {res.text}")

        return None
    else:
        log.error(
            f"Unhandled error code: [{res.status_code}: {res.reason_phrase}]: {res.text}"
        )

        return None

    # if save_to_db:
    #     if not db_engine:
    #         db_engine = db_depends.get_db_engine()

    #     errored: bool = False

    #     try:
    #         db_forecast_json = weather_forecast_dict_to_schema(
    #             weather_forecast_dict=decoded
    #         )
    #     except Exception as exc:
    #         msg = f"({type(exc)}) Error converting weather forecast to schema. Details: {exc}"
    #         log.error(msg)

    #         errored = True

    #     if not errored:
    #         try:
    #             save_forecast(
    #                 forecast_schema=db_forecast_json, engine=db_engine, echo=db_echo
    #             )
    #         except Exception as exc:
    #             msg = f"({type(exc)}) Error saving weather forecast to database. Details: {exc}"
    #             log.error(msg)

    #             errored = True

    #     if errored:
    #         log.warning("Errored while saving weather forecast to database.")

    # # log.debug(f"Decoded: {decoded}")

    # # location_schema: LocationIn = LocationIn.model_validate(decoded["location"])
    # # forecast_schema = ForecastJSONIn(forecast_json=decoded)

    # # api_response = APIResponseForecastWeather(
    # #     forecast=forecast_schema, location=location_schema
    # # )

    return decoded
