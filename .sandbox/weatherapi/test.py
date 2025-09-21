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
