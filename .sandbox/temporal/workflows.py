from datetime import timedelta
from temporalio import workflow, activity


@activity.defn
async def greet(name: str) -> str:
    return f"Hello, {name}!"


@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        greeting = await workflow.execute_activity(
            greet, name, start_to_close_timeout=timedelta(seconds=5)
        )

        return greeting
