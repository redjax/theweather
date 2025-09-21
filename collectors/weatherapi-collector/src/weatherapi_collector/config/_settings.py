from pathlib import Path

from shared.config import SHARED_CONFIG_DIR

from dynaconf import Dynaconf


__all__ = [
    "WEATHERAPI_SETTINGS",
]


## Set path to this directory
THIS_DIR: Path = Path(__file__).parent

## Set path to local config directory
WEATHERAPI_COLLECTOR_CONFIG_DIR: Path = THIS_DIR.parents[2] / "config"

## Create settings object
SETTINGS = Dynaconf(
    merge_enabled=True,
    envvar_prefix="WEATHERAPI_COLLECTOR",
    settings_files=[
        ## Shared config first, so local overwrites it
        str(SHARED_CONFIG_DIR / "settings.toml"),
        str(SHARED_CONFIG_DIR / ".secrets.toml"),
        "config/settings.toml",
        "config/.secrets.toml",
        "settings.toml",
        ".secrets.toml",
        str(WEATHERAPI_COLLECTOR_CONFIG_DIR / "settings.toml"),
        str(WEATHERAPI_COLLECTOR_CONFIG_DIR / ".secrets.toml"),
    ],
)

## Extract weatherapi settings from settings object
WEATHERAPI_SETTINGS = SETTINGS.get("weatherapi", {})
