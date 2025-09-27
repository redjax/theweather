from pathlib import Path
from dynaconf import Dynaconf
from shared.config import SHARED_CONFIG_DIR

__all__ = ["TEMPORAL_SETTINGS", "SETTINGS", "WEATHERAPI_SETTINGS"]

## Set path to this directory
THIS_DIR: Path = Path(__file__).parent

## Path to local config
CONFIG_DIR = THIS_DIR / "config"

SETTINGS = Dynaconf(
    merge_enabled=True,
    settings_files=[
        str(SHARED_CONFIG_DIR / "settings.toml"),
        str(SHARED_CONFIG_DIR / ".secrets.toml"),
        "config/settings.toml",
        "config/.secrets.toml",
        "settings.toml",
        ".secrets.toml",
        str(CONFIG_DIR / "settings.toml"),
        str(CONFIG_DIR / ".secrets.toml"),
    ],
)

## Extract temporal settings from settings object
TEMPORAL_SETTINGS = SETTINGS.get("temporal")

## Extract weatherapi settings from settings object
WEATHERAPI_SETTINGS = SETTINGS.get("weatherapi")
