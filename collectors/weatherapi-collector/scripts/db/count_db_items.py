from weatherapi_collector.depends import db_depends
from weatherapi_collector.domain import (
    CurrentWeatherJSONCollectorModel,
    CurrentWeatherJSONCollectorOut,
    CurrentWeatherJSONCollectorRepository,
    ForecastJSONCollectorRepository,
    ForecastJSONCollectorModel,
    ForecastJSONCollectorOut,
)

if __name__ == "__main__":
    print(f"Databases driver: {db_depends.get_db_engine().driver}")
    print(f"Database URL: {db_depends.get_db_engine().url}")

    with db_depends.get_session_pool()() as session:
        current_repo = CurrentWeatherJSONCollectorRepository(session)
        forecast_repo = ForecastJSONCollectorRepository(session)

        count_current_weather = current_repo.count()
        count_weather_forecast = forecast_repo.count()

        print(f"Current weather entities: {count_current_weather}")
        print(f"Weather forecast entities: {count_weather_forecast}")
