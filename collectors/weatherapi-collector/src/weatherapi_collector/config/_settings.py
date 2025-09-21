from pathlib import Path

from shared.config import SHARED_CONFIG_DIR

from dynaconf import Dynaconf


__all__ = [
    "SETTINGS",
]


THIS_DIR: Path = Path(__file__).parent

WEATHERAPI_COLLECTOR_CONFIG_DIR: Path = THIS_DIR.parents[2] / "config"

SETTINGS = Dynaconf(
    envvar_prefix="WEATHERAPI_COLLECTOR",
    settings_files=[
        ## Shared config first, so local overwrites it
        str(SHARED_CONFIG_DIR / "settings.toml"),
        str(SHARED_CONFIG_DIR / ".secrets.toml"),
        str(WEATHERAPI_COLLECTOR_CONFIG_DIR / "settings.toml"),
        str(WEATHERAPI_COLLECTOR_CONFIG_DIR / ".secrets.toml"),
    ],
)
