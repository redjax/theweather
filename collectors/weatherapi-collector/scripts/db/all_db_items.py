from weatherapi_collector import db_client
from weatherapi_collector.domain import (
    CurrentWeatherJSONCollectorModel,
    CurrentWeatherJSONCollectorOut,
)

all_current_weather_responses = db_client.get_all_current_weather_responses()
print(f"Retrieved {len(all_current_weather_responses)} current weather responses:")
for response in all_current_weather_responses:
    output_schema = CurrentWeatherJSONCollectorOut(
        current_weather_json=response.current_weather_json,
        id=response.id,
        created_at=response.created_at,
        retain=response.retain,
    )

    print(output_schema.model_dump_json(indent=2))
