from temporalio import activity
from weatherapi_collector import client as weatherapi_client


@activity.defn
def poll_weatherapi(api_key: str, location_name: str, days: int = 1):
    current_weather = weatherapi_client.get_current_weather(
        api_key=api_key, location=location_name
    )
    weather_forecast = weatherapi_client.get_weather_forecast(
        api_key=api_key, location=location_name, days=days
    )
    return {"current": current_weather, "forecast": weather_forecast}


@activity.defn
async def greet(name: str) -> str:
    return f"Hello, {name}!"
