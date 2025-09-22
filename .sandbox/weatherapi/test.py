import sys
from pathlib import Path

from shared.config import SHARED_SETTINGS
from shared.http_lib.config import HTTP_SETTINGS
from shared.depends import get_httpx_controller
from shared import http_lib
from shared.setup import setup_loguru_logging

from weatherapi_collector.config import (
    WEATHERAPI_SETTINGS,
    DB_SETTINGS as WEATHERAPI_COLLECTOR_DB_SETTINGS,
)
from weatherapi_collector import client as weatherapi_client

from loguru import logger as log

## Adjust number according to depth (sandbox/weatherapi/test.py -> up 3 to repo root)
repo_root = Path(__file__).parents[3]
shared_src = repo_root / "shared" / "src"

sys.path.insert(0, str(shared_src))

# -----------------------------------------------------

setup_loguru_logging()

log.info(f"\nShared settings: {SHARED_SETTINGS.as_dict()}")
log.info(f"\nWeatherAPI collector settings: {WEATHERAPI_SETTINGS}")
log.info(f"\nWeatherAPI collector DB settings: {WEATHERAPI_COLLECTOR_DB_SETTINGS}")
log.info(f"\nHTTP settings: {HTTP_SETTINGS}")

input("PAUSE")

http_controller = get_httpx_controller()

log.info(f"HTTP controller: {http_controller.__dict__}")

req = http_lib.build_request("HEAD", "https://www.google.com")

res = http_controller.send_request(req)

log.info(f"HTTP response: {res.status_code}: {res.reason_phrase}")

# ------------------------------------------------------

log.info(f"Get current weather for {WEATHERAPI_SETTINGS.get('LOCATION_NAME')}")
current_weather = weatherapi_client.get_current_weather()

log.info(f"Get weather forecast for {WEATHERAPI_SETTINGS.get('LOCATION_NAME')}")
forecast = weatherapi_client.get_weather_forecast(
    location=WEATHERAPI_SETTINGS.get("LOCATION_NAME")
)
