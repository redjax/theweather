import asyncio
import logging
import concurrent.futures
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import GreetingWorkflow, WeatherWorkflow, greet, poll_weatherapi
from _settings import TEMPORAL_SETTINGS


async def main():
    logging.basicConfig(level=logging.DEBUG)

    temporal_url = f"{TEMPORAL_SETTINGS.get('HOST')}:{TEMPORAL_SETTINGS.get('PORT')}"
    client = await Client.connect(
        temporal_url, namespace=TEMPORAL_SETTINGS.get("NAMESPACE", "default")
    )

    # Create ThreadPoolExecutor with sufficient workers for sync activities
    activity_executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    worker = Worker(
        client,
        task_queue="greeting-task-queue",
        workflows=[GreetingWorkflow, WeatherWorkflow],
        activities=[greet, poll_weatherapi],
        activity_executor=activity_executor,
    )

    print("Worker started and polling for tasks...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
