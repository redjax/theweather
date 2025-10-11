from __future__ import annotations

from weatherapi_collector.client import get_current_weather, get_weather_forecast

from loguru import logger as log
from temporalio import activity

__all__ = [
    "poll_current_weather",
    "poll_weather_forecast",
]


@activity.defn
def poll_current_weather(api_key: str, location: str) -> dict:
    result: dict = get_current_weather(api_key=api_key, location=location)

    return result


@activity.defn
def poll_weather_forecast(api_key: str, location: str, days: int = 1):
    result: dict = get_weather_forecast(api_key=api_key, location=location, days=days)

    return result
