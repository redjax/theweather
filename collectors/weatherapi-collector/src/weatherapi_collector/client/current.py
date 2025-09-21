from __future__ import annotations

import time

from shared import http_lib

# from weatherapi_collector.db_client.current_weather import (
#     save_current_weather,
#     save_current_weather_response
# )
from weatherapi_collector.config import WEATHERAPI_SETTINGS
from weatherapi_collector.constants import WEATHERAPI_BASE_URL
from weatherapi_collector.convert.methods import (
    current_weather_dict_to_schema,
    current_weather_response_dict_to_schema,
    location_dict_to_schema,
)

from . import requests

import hishel
import httpx
from loguru import logger as log
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

__all__ = ["get_current_weather"]


def get_current_weather(
    location: str = WEATHERAPI_SETTINGS.get("LOCATION_NAME"),
    api_key: str = WEATHERAPI_SETTINGS.get("API_KEY"),
    include_aqi: bool = True,
    headers: dict | None = None,
    use_cache: bool = False,
    retry: bool = True,
    max_retries: int = 3,
    retry_sleep: int = 5,
    retry_stagger: int = 3,
    save_to_db: bool = False,
    db_engine: sa.Engine | None = None,
    db_echo: bool = False,
) -> dict | None:
    """Get the current weather for a location.

    Params:
        location (str, optional): The location to get the current weather for. Defaults to location_name.
        api_key (str, optional): The API key to use. Defaults to api_key.
        include_aqi (bool, optional): Whether to include the air quality index. Defaults to True.
        headers (dict | None, optional): The headers to use. Defaults to None.
        use_cache (bool, optional): Whether to use the cache. Defaults to False.
        retry (bool, optional): Whether to retry the request. Defaults to True.
        max_retries (int, optional): The maximum number of retries to make. Defaults to 3.
        retry_sleep (int, optional): The number of seconds to sleep between retries. Defaults to 5.
        retry_stagger (int, optional): The number of seconds to stagger the retries. Defaults to 3.
        save_to_db (bool, optional): Whether to save the current weather to the database. Defaults to False.
        db_engine (Engine | None, optional): The database engine to use. If None, the default engine is used. Defaults to None.
        db_echo (bool, optional): Whether to echo SQL statements to the console. Defaults to False.

    Returns:
        dict | None: The current weather for the location.

    Raises:
        Exception: If there is an error getting the current weather, an `Exception` is raised.

    """
    if api_key is None or api_key == "":
        raise ValueError("WeatherAPI key is None or empty.")

    if not location or location == "":
        raise ValueError("Location name is required")

    current_weather_request: httpx.Request = requests.return_current_weather_request(
        api_key=api_key, location=location, include_aqi=include_aqi, headers=headers
    )

    log.info(f"Requesting current weather in location '{location}'")

    with http_lib.get_http_controller(use_cache=use_cache) as http:
        try:
            res: httpx.Response = http.client.send(current_weather_request)
            res.raise_for_status()
        except httpx.ReadTimeout as timeout:
            log.warning(
                f"({type(timeout)}) Operation timed out while requesting current weather."
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
                        res: httpx.Response = http.client.send(current_weather_request)
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
        log.info("Success requesting current weather")
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

    #     # log.warning("Saving current weather to database is not implemented")
    #     errored: bool = False

    #     ## Save current weather JSON response to database
    #     try:
    #         db_current_weather_json = current_weather_response_dict_to_schema(
    #             current_weather_response_dict=decoded
    #         )
    #     except Exception as exc:
    #         msg = f"({type(exc)}) Error converting current weather response to schema. Details: {exc}"
    #         log.error(msg)

    #         errored = True

    #     if not errored:
    #         try:
    #             save_current_weather_response(
    #                 current_weather_schema=db_current_weather_json,
    #                 engine=db_engine,
    #                 echo=db_echo,
    #             )
    #         except Exception as exc:
    #             msg = f"({type(exc)}) Error converting raw current weather response to schema. Details: {exc}"
    #             log.error(msg)

    #             errored = True

    #     if errored:
    #         log.warning(
    #             "Errored while saving raw current weather response to database."
    #         )

    #         return decoded

    #     try:
    #         db_location_in = location_dict_to_schema(location_dict=decoded["location"])
    #     except Exception as exc:
    #         msg = f"({type(exc)}) Error converting decoded response to schema. Details: {exc}"
    #         log.error(msg)

    #         errored = True

    #     if not errored:
    #         try:
    #             db_current_weather_in = current_weather_dict_to_schema(
    #                 current_weather_dict=decoded["current"]
    #             )
    #         except Exception as exc:
    #             msg = f"({type(exc)}) Error converting decoded response to schema. Details: {exc}"
    #             log.error(msg)

    #             errored = True

    #     if not errored:
    #         ## Save current weather to database
    #         try:
    #             db_current_weather_out = save_current_weather(
    #                 location=db_location_in,
    #                 current_weather=db_current_weather_in,
    #                 engine=db_engine,
    #                 echo=db_echo,
    #             )
    #             log.success("Saved current weather to database")
    #             log.debug(f"Current weather from database: {db_current_weather_out}")
    #         except Exception as exc:
    #             msg = f"({type(exc)}) Error saving current weather to database: {exc}"
    #             log.error(msg)

    #             errored = True

    #     if errored:
    #         log.warning(
    #             "Errored while saving current weather and/or location to database."
    #         )

    return decoded
