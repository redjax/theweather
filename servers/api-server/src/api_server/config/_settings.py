from __future__ import annotations

import typing as t
from pathlib import Path

from shared.config import SHARED_CONFIG_DIR

from dynaconf import Dynaconf

__all__ = [
    "APISERVER_CONFIG_DIR",
    "SETTINGS",
    "LOGGING_SETTINGS",
    "DB_SETTINGS",
    "FASTAPI_SETTINGS",
    "UVICORN_SETTINGS",
]


## Set path to this directory
THIS_DIR: Path = Path(__file__).parent

## Set path to local config directory
APISERVER_CONFIG_DIR: Path = THIS_DIR.parents[2] / "config"

## Create settings object
SETTINGS = Dynaconf(
    merge_enabled=True,
    envvar_prefix="APISERVER",
    settings_files=[
        ## Shared config first, so local overwrites it
        str(SHARED_CONFIG_DIR / "settings.toml"),
        str(SHARED_CONFIG_DIR / ".secrets.toml"),
        "config/settings.toml",
        "config/.secrets.toml",
        "settings.toml",
        ".secrets.toml",
        str(APISERVER_CONFIG_DIR / "settings.toml"),
        str(APISERVER_CONFIG_DIR / ".secrets.toml"),
    ],
)

## Extract weatherapi settings from settings object
LOGGING_SETTINGS = SETTINGS.get("logging", {})

## Extract database settings from settings object
DB_SETTINGS = SETTINGS.get("database", {})

## Extract FastAPI settings from settings object
FASTAPI_SETTINGS = SETTINGS.get("fastapi", {})

## Extract Uvicorn settings from settings object
UVICORN_SETTINGS = SETTINGS.get("uvicorn", {})
