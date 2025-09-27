import logging
from _settings import SETTINGS, TEMPORAL_SETTINGS
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import GreetingWorkflow, greet


async def main():
    print("Starting temporal server")

    temporal_url = f"{TEMPORAL_SETTINGS.get('HOST')}:{TEMPORAL_SETTINGS.get('PORT')}"
    print(f"  Temporal URL: {temporal_url}")

    # Connect to Temporal server with namespace if you use one
    client = await Client.connect(
        temporal_url, namespace=TEMPORAL_SETTINGS.get("NAMESPACE", "default")
    )

    # Use async with context manager to ensure clean worker startup and shutdown
    async with Worker(
        client,
        task_queue="greeting-task-queue",
        workflows=[GreetingWorkflow],
        activities=[greet],
    ):
        print("Worker started. Listening for tasks...")
        # Just wait forever, the Worker is running until this coroutine exits
        await asyncio.Event().wait()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(main())
