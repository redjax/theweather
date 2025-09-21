import sys
from pathlib import Path

## Adjust number according to depth (sandbox/weatherapi/test.py -> up 3 to repo root)
repo_root = Path(__file__).parents[3]
shared_src = repo_root / "shared" / "src"

sys.path.insert(0, str(shared_src))

from shared.config import SHARED_SETTINGS

print(f"Shared settings: {SHARED_SETTINGS.as_dict()}")
