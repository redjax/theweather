import sys
from pathlib import Path

from shared.config import SHARED_SETTINGS
from shared.http_lib.config import HTTP_SETTINGS
from shared.depends import get_httpx_controller
from shared import http_lib

from weatherapi_collector.config import WEATHERAPI_SETTINGS
from weatherapi_collector import client as weatherapi_client

## Adjust number according to depth (sandbox/weatherapi/test.py -> up 3 to repo root)
repo_root = Path(__file__).parents[3]
shared_src = repo_root / "shared" / "src"

sys.path.insert(0, str(shared_src))

# -----------------------------------------------------

print(f"\nShared settings: {SHARED_SETTINGS.as_dict()}")
print(f"\nWeatherAPI collector settings: {WEATHERAPI_SETTINGS}")
print(f"\nHTTP settings: {HTTP_SETTINGS}")

http_controller = get_httpx_controller()

print(f"HTTP controller: {http_controller.__dict__}")

req = http_lib.build_request("HEAD", "https://www.google.com")

res = http_controller.send_request(req)

print(f"HTTP response: {res.status_code}: {res.reason_phrase}")

# ------------------------------------------------------

print(f"Get current weather for {WEATHERAPI_SETTINGS.get('LOCATION_NAME')}")
current_weather = weatherapi_client.get_current_weather()

print(f"Get weather forecast for {WEATHERAPI_SETTINGS.get('LOCATION_NAME')}")
forecast = weatherapi_client.get_weather_forecast(
    location=WEATHERAPI_SETTINGS.get("LOCATION_NAME")
)
