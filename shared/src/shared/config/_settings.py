from pathlib import Path

from dynaconf import Dynaconf


__all__ = ["SHARED_SETTINGS"]

THIS_DIR: Path = Path(__file__).parent

shared_config_dir = THIS_DIR.parents[2] / "config"

SHARED_SETTINGS: Dynaconf = Dynaconf(
    settings_files=[
        str(shared_config_dir / "settings.toml"),
        str(shared_config_dir / ".secrets.toml"),
    ]
)
