from pathlib import Path

from shared.config import SHARED_SETTINGS

__all__ = ["HTTP_SETTINGS"]

## Extract http settings from shared config
HTTP_SETTINGS = SHARED_SETTINGS.get("http", {})
