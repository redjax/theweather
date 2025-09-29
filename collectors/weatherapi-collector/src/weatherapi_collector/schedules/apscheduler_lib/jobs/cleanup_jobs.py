from loguru import logger as log
from weatherapi_collector import db_client
import asyncio

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
