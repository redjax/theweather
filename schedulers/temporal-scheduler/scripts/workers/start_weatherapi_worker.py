from temporal_scheduler.config import (
    DB_SETTINGS,
    TEMPORAL_SETTINGS,
    WEATHERAPI_SETTINGS,
)
from temporal_scheduler.weatherapi import start_worker

if __name__ == "__main__":
    print(f"DB settings: {DB_SETTINGS}")
    print(f"Temporal settings: {TEMPORAL_SETTINGS}")
    print(f"WeatherAPI settings: {WEATHERAPI_SETTINGS}")

    start_worker()
