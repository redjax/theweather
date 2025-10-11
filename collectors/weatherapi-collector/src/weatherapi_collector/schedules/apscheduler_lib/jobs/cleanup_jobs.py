from __future__ import annotations

import asyncio

from weatherapi_collector import db_client

from loguru import logger as log

__all__ = ["job_vacuum_current_weather_json_responses"]


async def job_vacuum_current_weather_json_responses(db_echo: bool = False) -> None:
    log.info("[APScheduler] Vacuuming weather JSON responses")

    try:
        deleted_rows = await asyncio.to_thread(
            db_client.vacuum_current_weather_json_responses, db_echo
        )
        log.info(f"Vacuumed {deleted_rows} rows")
    except Exception as e:
        log.error(f"Error during vacuuming: {e}")


async def job_vacuum_forecast_weather_json_responses(db_echo: bool = False) -> None:
    log.info("[APScheduler] Vacuuming forecast weather JSON responses")

    try:
        deleted_rows = await asyncio.to_thread(
            db_client.vacuum_forecast_weather_json_responses, db_echo
        )
        log.info(f"Vacuumed {deleted_rows} rows")
    except Exception as e:
        log.error(f"Error during vacuuming: {e}")
