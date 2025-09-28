from datetime import timedelta
from temporalio import workflow

## Import activities with sandbox passthrough.
#  This is to allow for things like loading Dynaconf configs
with workflow.unsafe.imports_passed_through():
    from temporal_scheduler.weatherapi.activities import (
        poll_current_weather,
        poll_weather_forecast,
    )


__all__ = [
    "WeatherWorkflow",
]


@workflow.defn
class WeatherWorkflow:
    @workflow.run
    async def run(self, input: dict) -> dict:
        current = await workflow.execute_activity(
            poll_current_weather,
            args=(input["api_key"], input["location"]),
            start_to_close_timeout=timedelta(seconds=20),
        )
        forecast = await workflow.execute_activity(
            poll_weather_forecast,
            args=(input["api_key"], input["location"], input.get("days", 1)),
            start_to_close_timeout=timedelta(seconds=20),
        )

        return {"current_result": current, "forecast_result": forecast}
