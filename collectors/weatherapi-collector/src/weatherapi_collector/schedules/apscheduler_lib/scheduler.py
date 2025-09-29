import typing as t

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
from loguru import logger as log

from weatherapi_collector.schedules.apscheduler_lib.jobs.http_jobs import (
    job_weatherapi_current_weather,
    job_weatherapi_weather_forecast,
)
from weatherapi_collector.schedules.apscheduler_lib.jobs.data_jobs import (
    job_post_weather_readings,
)
from weatherapi_collector.schedules.apscheduler_lib.jobs.cleanup_jobs import (
    job_vacuum_current_weather_json_responses,
)

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
    cron_schedules: t.Optional[dict[str, dict[str, t.Any]]] = None,
):
    _weatherapi_schedule = cron_schedules.get("weatherapi_jobs", {})
    _data_jobs_schedule = cron_schedules.get("data_jobs", {})
    _cleanup_jobs_schedule = cron_schedules.get("cleanup_jobs", {})

    scheduler = AsyncIOScheduler()

    ## Weather jobs (quarter-hourly)
    scheduler.add_job(
        job_weatherapi_current_weather,
        trigger=CronTrigger(**{**default_cron_schedule, **_weatherapi_schedule}),
        args=[location_name, api_key, save_to_db, db_echo],
        id="weatherapi_current_weather",
    )
    scheduler.add_job(
        job_weatherapi_weather_forecast,
        trigger=CronTrigger(**{**default_cron_schedule, **_weatherapi_schedule}),
        args=[location_name, api_key, forecast_days, save_to_db, db_echo],
        id="weatherapi_forecast",
    )

    ## Data posting jobs (every 20 min)
    scheduler.add_job(
        job_post_weather_readings,
        trigger=CronTrigger(**{**default_cron_schedule, **_data_jobs_schedule}),
        args=[db_echo],
        id="post_weather_readings",
    )

    ## Cleanup jobs (every 10 min)
    scheduler.add_job(
        job_vacuum_current_weather_json_responses,
        args=[db_echo],
        trigger=CronTrigger(**{**default_cron_schedule, **_cleanup_jobs_schedule}),
        id="vacuum_cleanup",
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
