from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf

__all__ = [
    "LOGGING_SETTINGS",
    "DB_SETTINGS",
]


## Create settings object
SETTINGS = Dynaconf(
    merge_enabled=True,
    envvar_prefix="DB_OPERATOR",
    settings_files=[
        ## Shared config first, so local overwrites it
        "config/settings.toml",
        "config/.secrets.toml",
        "settings.toml",
        ".secrets.toml",
    ],
)

## Extract weatherapi settings from settings object
LOGGING_SETTINGS = SETTINGS.get("logging", {})

## Extract database settings from settings object
DB_SETTINGS = SETTINGS.get("database", {})
