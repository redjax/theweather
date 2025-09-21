from pathlib import Path

from dynaconf import Dynaconf


__all__ = ["SHARED_SETTINGS", "SHARED_CONFIG_DIR"]

THIS_DIR: Path = Path(__file__).parent

## Set shared config directory
SHARED_CONFIG_DIR = THIS_DIR.parents[2] / "config"

SHARED_SETTINGS: Dynaconf = Dynaconf(
    settings_files=[
        str(SHARED_CONFIG_DIR / "settings.toml"),
        str(SHARED_CONFIG_DIR / ".secrets.toml"),
        "settings.toml",
        ".secrets.toml",
        "config/settings.toml",
        "config/.secrets.toml",
    ],
)
