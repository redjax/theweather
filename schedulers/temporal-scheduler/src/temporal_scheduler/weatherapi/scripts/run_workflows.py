import asyncio
import uuid

from shared.setup import setup_loguru_logging
from temporal_scheduler.weatherapi.workflows import WeatherWorkflow
from temporal_scheduler.config import (
    TEMPORAL_SETTINGS,
    WEATHERAPI_SETTINGS,
)

from temporalio.client import Client
from loguru import logger as log


__all__ = ["run_weatherapi_workflow"]


async def run_weatherapi_workflow():
    temporal_url = f"{TEMPORAL_SETTINGS.get('HOST')}:{TEMPORAL_SETTINGS.get('PORT')}"

    client = await Client.connect(temporal_url, namespace="weatherapi")

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
