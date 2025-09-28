import asyncio
import concurrent.futures
import logging

from temporalio.client import Client
from temporalio.worker import Worker

# ADD these imports:
from temporalio.worker.workflow_sandbox import (
    SandboxedWorkflowRunner,
    SandboxRestrictions,
)

from weatherapi_collector.schedules.temporal.workflows import WeatherWorkflow
from weatherapi_collector.schedules.temporal.activities import (
    poll_current_weather,
    poll_weather_forecast,
)
from weatherapi_collector.config._settings import TEMPORAL_SETTINGS

from loguru import logger as log


async def main():
    logging.basicConfig(level=TEMPORAL_SETTINGS.get("LOG_LEVEL", "INFO"))

    temporal_url = f"{TEMPORAL_SETTINGS.get('HOST')}:{TEMPORAL_SETTINGS.get('PORT')}"
    client = await Client.connect(
        temporal_url, namespace=TEMPORAL_SETTINGS.get("NAMESPACE", "default")
    )

    activity_executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    # Add your modules as passthrough -- include any that transitively cause errors
    # E.g., dynaconf, ruamel.yaml, weatherapi_collector, etc.
    my_restrictions = SandboxRestrictions.default.with_passthrough_modules(
        "weatherapi_collector", "dynaconf", "shared"
    )

    worker = Worker(
        client,
        task_queue="weatherapi-task-queue",
        workflows=[WeatherWorkflow],
        activities=[poll_current_weather, poll_weather_forecast],
        activity_executor=activity_executor,
        workflow_runner=SandboxedWorkflowRunner(restrictions=my_restrictions),
    )

    log.info("Temporal worker started and polling task queue...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
