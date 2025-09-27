import asyncio
from temporalio.client import Client
from workflows import GreetingWorkflow
from _settings import TEMPORAL_SETTINGS


async def main():
    temporal_url = f"{TEMPORAL_SETTINGS.get('HOST')}:{TEMPORAL_SETTINGS.get('PORT')}"
    namespace = TEMPORAL_SETTINGS.get("NAMESPACE", "default")

    client = await Client.connect(temporal_url, namespace=namespace)

    result = await client.execute_workflow(
        GreetingWorkflow.run,
        "Temporal",
        id="greeting-workflow-id",
        task_queue="greeting-task-queue",
    )
    print(f"Workflow result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
