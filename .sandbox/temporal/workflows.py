from datetime import timedelta
import typing as t
from temporalio import workflow

# Assume poll_weatherapi is imported safely or passed through the sandbox
with workflow.unsafe.imports_passed_through():
    from activities import poll_weatherapi, greet


@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            greet, name, start_to_close_timeout=timedelta(seconds=5)
        )


@workflow.defn
class WeatherWorkflow:
    @workflow.run
    async def run(self, input: t.Dict[str, str]) -> t.Any:
        return await workflow.execute_activity(
            poll_weatherapi,
            args=(input["api_key"], input["location_name"]),
            start_to_close_timeout=timedelta(seconds=30),
        )
