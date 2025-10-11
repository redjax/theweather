from __future__ import annotations

import typing as t

from weatherapi_collector import db_client
from weatherapi_collector.domain import (
    CurrentWeatherJSONCollectorIn,
    CurrentWeatherJSONCollectorModel,
    CurrentWeatherJSONCollectorOut,
    CurrentWeatherJSONCollectorRepository,
)

from loguru import logger as log

__all__ = [
    "job_vacuum_current_weather_json_responses",
]


def job_vacuum_current_weather_json_responses(echo: bool = False) -> dict[str, bool]:
    log.info("Vacuuming current weather JSON responses from the DB")

    job_results = {"current_weather_json_responses": {"success": False, "deleted": []}}

    try:
        deleted = db_client.vacuum_current_weather_json_responses(echo=echo)
        log.info(
            f"Current weather JSON responses vacuum complete. Rows deleted: {deleted}"
        )

        job_results["current_weather_json_responses"]["success"] = True
        job_results["current_weather_json_responses"]["deleted"] = deleted
    except Exception as exc:
        log.error(f"Error vacuuming current weather JSON responses from DB: {exc}")
        raise

    return job_results
