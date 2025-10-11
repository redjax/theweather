from __future__ import annotations

import asyncio
import uuid

from weatherapi_collector.config._settings import (
    SETTINGS,
    TEMPORAL_SETTINGS,
    WEATHERAPI_SETTINGS,
)
from weatherapi_collector.schedules.temporal.workflows import WeatherWorkflow

from loguru import logger as log
from shared.setup import setup_loguru_logging
from temporalio.client import Client

__all__ = ["run_weather_workflow"]


async def run_weather_workflow():
    temporal_url = f"{TEMPORAL_SETTINGS.get('HOST')}:{TEMPORAL_SETTINGS.get('PORT')}"
    client = await Client.connect(
        temporal_url, namespace=TEMPORAL_SETTINGS.get("NAMESPACE", "default")
    )

    workflow_id = f"weather-workflow-{uuid.uuid4()}"
    result = await client.execute_workflow(
        WeatherWorkflow.run,
        {
            "api_key": WEATHERAPI_SETTINGS.get("API_KEY"),
            "location": WEATHERAPI_SETTINGS.get("LOCATION_NAME"),
            "days": 1,
        },
        id=workflow_id,
        task_queue="weatherapi-task-queue",
    )
    print("Workflow result:", result)


if __name__ == "__main__":
    setup_loguru_logging()
    asyncio.run(run_weather_workflow())
