from __future__ import annotations

import asyncio

from weatherapi_collector import (
    client as weatherapi_client,
    db_client,
)
from weatherapi_collector.depends import get_db_engine

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger as log

__all__ = ["job_weatherapi_current_weather", "job_weatherapi_weather_forecast"]


async def job_weatherapi_current_weather(
    location_name: str, api_key: str, save_to_db: bool = False, db_echo: bool = False
):
    log.info(f"[APScheduler] Collect current weather for {location_name}")
    data = await asyncio.to_thread(
        weatherapi_client.get_current_weather, location_name, api_key, db_echo
    )
    if save_to_db:
        engine = get_db_engine()
        await asyncio.to_thread(db_client.save_current_weather_response, data, db_echo)


async def job_weatherapi_weather_forecast(
    location_name: str,
    api_key: str,
    forecast_days: int = 1,
    save_to_db: bool = False,
    db_echo: bool = False,
):
    log.info(f"[APScheduler] Collect forecast for {location_name}")
    result = await asyncio.to_thread(
        weatherapi_client.get_weather_forecast,
        location_name,
        forecast_days,
        api_key,
        db_echo=db_echo,
    )
    if save_to_db:
        engine = get_db_engine()
        await asyncio.to_thread(db_client.save_forecast, result, db_echo)
