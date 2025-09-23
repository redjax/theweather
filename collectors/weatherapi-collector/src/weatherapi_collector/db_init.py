from pathlib import Path
from shared.db import Base, create_base_metadata
from shared.domain.weatherapi.location import LocationJSONModel
from shared.domain.weatherapi.weather import ForecastJSONModel, CurrentWeatherJSONModel

from weatherapi_collector.depends.db_depends import get_db_engine
from weatherapi_collector.config import DB_SETTINGS

from loguru import logger as log

__all__ = ["initialize_database"]


def initialize_database():
    """Initialize database by creating Base metadata."""

    if DB_SETTINGS.get("DB_TYPE") == "sqlite":
        _db_path = Path(DB_SETTINGS.get("DB_DATABASE")).parent

        if not _db_path.exists():
            log.warning(f"Database directory '{_db_path}' does not exist. Creating")
            try:
                _db_path.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                log.error(f"Failed to create database directory: {exc}")
                raise

    engine = get_db_engine()

    tables_to_create = [
        ForecastJSONModel.__table__,
        CurrentWeatherJSONModel.__table__,
    ]

    log.info(f"Initializing database at {engine.url}")
    try:
        create_base_metadata(base=Base, engine=engine, tables=tables_to_create)
        log.info(f"Database initialized")
    except Exception as e:
        log.error(f"Failed to initialize database: {e}")
        raise
