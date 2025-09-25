from shared.domain.collectors.payloads import WeatherCollectorPayloadIn
from weatherapi_collector import client as weatherapi_client
from weatherapi_collector.config import WEATHERAPI_SETTINGS

import httpx

req = httpx.Request("GET", url="http://127.0.0.1:8000/health")

API_HEALTHY: bool = False
API_BASE_URL: str = "http://127.0.0.1:8000/api/v1"


with httpx.Client() as client:
    res = client.send(req)
    res.raise_for_status()

    print(
        f"API server healthcheck: [{res.status_code}: {res.reason_phrase}]: {res.text}"
    )
    if res.status_code == 200:
        API_HEALTHY = True

print(f"API server healthy: {API_HEALTHY}")

if not API_HEALTHY:
    raise Exception("API server not healthy")

print(f"WeatherAPI settings: {WEATHERAPI_SETTINGS}")

try:
    current_weather = weatherapi_client.get_current_weather()
except Exception as exc:
    print(f"[ERROR] Failed requesting WeatherAPI current weather: ({type(exc)}) {exc}")
    raise

ex_payload: WeatherCollectorPayloadIn = WeatherCollectorPayloadIn(
    source="weatherapi",
    label="test",
    data=current_weather,
)

req = httpx.Request(
    "POST",
    url=f"{API_BASE_URL}/collectors/weather",
    json=ex_payload.model_dump(),
)

print(f"Sending example metrics: {ex_payload.model_dump()}")
with httpx.Client() as client:
    res = client.send(req)
    res.raise_for_status()

    print(
        f"WeatherAPI current weather metrics sent: [{res.status_code}: {res.reason_phrase}]: {res.text}"
    )
