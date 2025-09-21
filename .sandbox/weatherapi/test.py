import sys
from pathlib import Path

## Adjust number according to depth (sandbox/weatherapi/test.py -> up 3 to repo root)
repo_root = Path(__file__).parents[3]
shared_src = repo_root / "shared" / "src"

sys.path.insert(0, str(shared_src))

# -----------------------------------------------------

from shared.config import SHARED_SETTINGS
from weatherapi_collector.config import WEATHERAPI_SETTINGS
from shared.http_lib.config import HTTP_SETTINGS

print(f"\nShared settings: {SHARED_SETTINGS.as_dict()}")
print(f"\nWeatherAPI collector settings: {WEATHERAPI_SETTINGS}")
print(f"\nHTTP settings: {HTTP_SETTINGS}")

from shared import http_lib

http_controller = http_lib.HttpxController(
    use_cache=HTTP_SETTINGS.get("HTTP_USE_CACHE"),
    cache_type=HTTP_SETTINGS.get("HTTP_CACHE_TYPE"),
    follow_redirects=True,
    cache_file_dir=HTTP_SETTINGS.get("HTTP_CACHE_FILE_DIR"),
    cache_db_file=HTTP_SETTINGS.get("HTTP_CACHE_DB_FILE"),
    cache_ttl=HTTP_SETTINGS.get("HTTP_CACHE_CHECK_TTL_EVERY"),
)

print(f"HTTP controller: {http_controller.__dict__}")

req = http_lib.build_request("HEAD", "https://www.google.com")

res = http_controller.send_request(req)

print(f"HTTP response: {res.status_code}: {res.reason_phrase}")
