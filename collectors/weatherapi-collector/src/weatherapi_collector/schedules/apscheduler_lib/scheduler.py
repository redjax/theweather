from __future__ import annotations

import asyncio
import typing as t

from weatherapi_collector.schedules.apscheduler_lib.jobs.cleanup_jobs import (
    job_vacuum_current_weather_json_responses,
    job_vacuum_forecast_weather_json_responses,
)
from weatherapi_collector.schedules.apscheduler_lib.jobs.data_jobs import (
    job_post_weather_readings,
)
from weatherapi_collector.schedules.apscheduler_lib.jobs.http_jobs import (
    job_weatherapi_current_weather,
    job_weatherapi_weather_forecast,
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger as log

__all__ = [
    "setup_schedule",
    "start_scheduler",
    "default_cron_schedule",
]

## Provide defaults for all cron fields as None
default_cron_schedule = {
    "year": None,
    "month": None,
    "day": None,
    "week": None,
    "day_of_week": None,
    "hour": None,
    "minute": None,
    "second": None,
    "start_date": None,
    "end_date": None,
    "timezone": None,
    "jitter": None,
}


def setup_schedule(
    location_name: str,
    api_key: str,
    forecast_days: int = 1,
    save_to_db: bool = False,
    db_echo: bool = False,
    cron_schedules: t.Optional[dict[str, t.Any]] = None,
):
    scheduler = AsyncIOScheduler()

    def make_trigger(value):
        # Accept both dicts and full cron string expressions
        if isinstance(value, str):
            return CronTrigger.from_crontab(value)
        elif isinstance(value, dict):
            return CronTrigger(**{**default_cron_schedule, **value})
        else:
            raise TypeError(f"Unsupported cron schedule type: {type(value)}")

    _weatherapi_schedule = cron_schedules.get("weatherapi_jobs")
    _data_jobs_schedule = cron_schedules.get("data_jobs")
    _cleanup_jobs_schedule = cron_schedules.get("cleanup_jobs")

    # Create triggers dynamically
    weather_trigger = make_trigger(_weatherapi_schedule)
    data_trigger = make_trigger(_data_jobs_schedule)
    cleanup_trigger = make_trigger(_cleanup_jobs_schedule)

    # Add jobs
    scheduler.add_job(
        job_weatherapi_current_weather,
        trigger=weather_trigger,
        args=[location_name, api_key, save_to_db, db_echo],
        id="weatherapi_current_weather",
    )
    scheduler.add_job(
        job_weatherapi_weather_forecast,
        trigger=weather_trigger,
        args=[location_name, api_key, forecast_days, save_to_db, db_echo],
        id="weatherapi_forecast",
    )
    scheduler.add_job(
        job_post_weather_readings,
        trigger=data_trigger,
        args=[db_echo],
        id="post_weather_readings",
    )
    scheduler.add_job(
        job_vacuum_current_weather_json_responses,
        trigger=cleanup_trigger,
        args=[db_echo],
        id="weatherapi_current_weather_vacuum",
    )
    scheduler.add_job(
        job_vacuum_forecast_weather_json_responses,
        trigger=cleanup_trigger,
        args=[db_echo],
        id="weatherapi_forecast_vacuum",
    )

    return scheduler


async def _start_scheduler(
    schedules_dict: dict[str, dict[str, t.Any]],
    location_name,
    api_key,
    forecast_days=1,
    save_to_db=False,
    db_echo: bool = False,
):
    scheduler = setup_schedule(
        location_name=location_name,
        api_key=api_key,
        forecast_days=forecast_days,
        save_to_db=save_to_db,
        db_echo=db_echo,
        cron_schedules=schedules_dict,
    )

    scheduler.start()

    log.info("APScheduler started")

    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        log.warning("Scheduler stopped by cancellation")
    except KeyboardInterrupt:
        log.warning("Scheduler stopped by CTRL+C")
        pass
    except Exception as e:
        log.error(f"Scheduler stopped due to error: {e}")


def start_scheduler(
    schedules_dict: dict[str, dict[str, t.Any]],
    location_name,
    api_key,
    forecast_days=1,
    save_to_db=False,
    db_echo: bool = False,
):
    log.debug(f"APScheduler schedules: {schedules_dict}")

    try:
        asyncio.run(
            _start_scheduler(
                schedules_dict,
                location_name,
                api_key,
                forecast_days,
                save_to_db,
                db_echo=db_echo,
            )
        )
    except KeyboardInterrupt:
        log.warning("Scheduler stopped by CTRL+C")
    except Exception as e:
        log.error(f"Scheduler stopped due to error: {e}")
