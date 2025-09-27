import asyncio
import uuid
from temporalio.client import Client
from workflows import GreetingWorkflow, WeatherWorkflow
from _settings import TEMPORAL_SETTINGS, WEATHERAPI_SETTINGS


async def main():
    temporal_url = f"{TEMPORAL_SETTINGS.get('HOST')}:{TEMPORAL_SETTINGS.get('PORT')}"
    namespace = TEMPORAL_SETTINGS.get("NAMESPACE", "default")

    api_key = WEATHERAPI_SETTINGS.get("API_KEY")
    location = WEATHERAPI_SETTINGS.get("LOCATION_NAME")

    workflow_id = f"weather-workflow-{uuid.uuid4()}"

    client = await Client.connect(temporal_url, namespace=namespace)

    greeting_result = await client.execute_workflow(
        GreetingWorkflow.run,
        "Temporal",
        id="greeting-workflow-id",
        task_queue="greeting-task-queue",
    )
    print(f"Greeting Workflow result: {greeting_result}")

    weather_result = await client.execute_workflow(
        WeatherWorkflow.run,
        {
            "api_key": api_key,
            "location_name": location,
        },
        id=workflow_id,
        task_queue="greeting-task-queue",
    )
    print(f"Weather Workflow result: {weather_result}")


if __name__ == "__main__":
    asyncio.run(main())
