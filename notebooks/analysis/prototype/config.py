from dynaconf import Dynaconf

__all__ = ["SETTINGS", "DB_SETTINGS"]

SETTINGS = Dynaconf(
    merge_enabled = True,
    settings_files=[
        "config/settings.toml",
        "config/.secrets.toml",
        "settings.toml",
        ".secrets.toml"
    ]
)

DB_SETTINGS = SETTINGS.get("DATABASE", {})