from __future__ import annotations

from weatherapi_collector.constants import WEATHERAPI_BASE_URL

from shared import http_lib
import httpx
from loguru import logger as log

__all__ = [
    "return_current_weather_request",
    "return_weather_forecast_request",
]


def return_current_weather_request(
    api_key: str, location: str, include_aqi: bool = False, headers: dict | None = None
) -> httpx.Request:
    """Return an httpx.Request object for the current weather.

    Params:
        api_key (str): The API key to use.
        location (str): The location to get the current weather for.
        include_aqi (bool, optional): Whether to include the air quality index. Defaults to False.
        headers (dict | None, optional): The headers to use. Defaults to None.

    """
    url: str = f"{WEATHERAPI_BASE_URL}/current.json"
    params: dict = {
        "key": api_key,
        "q": location,
        "aqi": f"{'yes' if include_aqi else 'no'}",
    }

    log.debug(f"Building WeatherAPI current weather request")
    req: httpx.Request = http_lib.build_request(url=url, params=params, headers=headers)

    return req


def return_weather_forecast_request(
    api_key: str,
    location: str,
    days: int = 1,
    include_aqi: bool = False,
    include_alerts: bool = False,
    headers: dict | None = None,
) -> httpx.Request:
    """Return an httpx.Request object for the weather forecast.

    Params:
        api_key (str): The API key to use.
        location (str): The location to get the weather forecast for.
        days (int, optional): The number of days to get the weather forecast for. Defaults to 1.
        include_aqi (bool, optional): Whether to include the air quality index. Defaults to False.
        include_alerts (bool, optional): Whether to include the alerts. Defaults to False.
        headers (dict | None, optional): The headers to use. Defaults to None.

    Returns:
        httpx.Request: The httpx.Request object for the weather forecast.

    Raises:
        Exception: If there is an error building the httpx.Request object, an `Exception` is raised.

    """
    url: str = f"{WEATHERAPI_BASE_URL}/forecast.json"
    params: dict = {
        "key": api_key,
        "q": location,
        "aqi": f"{'yes' if include_aqi else 'no'}",
        "alerts": f"{'yes' if include_alerts else 'no'}",
        "days": days,
    }

    log.debug(f"Building WeatherAPI weather forecast request")
    req: httpx.Request = http_lib.build_request(url=url, params=params, headers=headers)

    return req
