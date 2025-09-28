from weatherapi_collector.config import DB_SETTINGS
from weatherapi_collector.depends import db_depends
from weatherapi_collector.domain import (
    CurrentWeatherJSONCollectorIn,
    CurrentWeatherJSONCollectorModel,
    CurrentWeatherJSONCollectorOut,
    CurrentWeatherJSONCollectorRepository,
    ForecastJSONCollectorIn,
    ForecastJSONCollectorModel,
    ForecastJSONCollectorOut,
    ForecastJSONCollectorRepository,
)
from weatherapi_collector.db_client import get_all_current_weather
from sqlalchemy import inspect

engine = db_depends.get_db_engine()
inspector = inspect(engine)

print(engine.url)

for tbl in inspector.get_table_names():
    print(f"Table: {tbl}")
    columns = inspector.get_columns(tbl)
    for column in columns:
        print(f"  Column: {column['name']} - {column['type']}")

current_weather_readings_list = get_all_current_weather(engine=engine)
print(f"Retrieved {len(current_weather_readings_list)} current weather readings:")

# SessionLocal = db_depends.get_session_pool()

# with SessionLocal() as session:
#     current_weather_repo = CurrentWeatherJSONCollectorRepository(session)
#     forecast_repo = ForecastJSONCollectorRepository(session)

#     current_weather_items = current_weather_repo.list()
#     # forecast_items = forecast_repo.get_all()

#     print("Current Weather Items:")
#     for item in current_weather_items:
#         print(item)

#     # print("\nForecast Items:")
#     # for item in forecast_items:
#     #     print(item)
