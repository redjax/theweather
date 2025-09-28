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

from temporal_scheduler.weatherapi.workflows import WeatherWorkflow
from temporal_scheduler.weatherapi.activities import (
    poll_current_weather,
    poll_weather_forecast,
)
from temporal_scheduler.config._settings import TEMPORAL_SETTINGS
from temporal_scheduler.constants import ALLOWED_LIBS

from loguru import logger as log

__all__ = ["start_worker"]


async def main():
    logging.basicConfig(level=TEMPORAL_SETTINGS.get("LOG_LEVEL", "INFO"))

    temporal_url = f"{TEMPORAL_SETTINGS.get('HOST')}:{TEMPORAL_SETTINGS.get('PORT')}"
    client = await Client.connect(temporal_url, namespace="weatherapi")

    activity_executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    # Add your modules as passthrough -- include any that transitively cause errors
    # E.g., dynaconf, ruamel.yaml, weatherapi_collector, etc.
    my_restrictions = SandboxRestrictions.default.with_passthrough_modules(
        *ALLOWED_LIBS
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


def start_worker():
    log.debug("DEBUG logging enabled")

    log.debug(f"Temporal settings: {TEMPORAL_SETTINGS}")

    log.info("Starting Temporal worker")
    try:
        asyncio.run(main())
    except Exception as exc:
        log.error(f"Temporal worker exited unsuccessfuly: ({type(exc).__name__}) {exc}")
        raise
    except KeyboardInterrupt:
        log.warning("Temporal worker operation cancelled by user")
        return


if __name__ == "__main__":
    start_worker()
