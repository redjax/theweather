from __future__ import annotations

from pathlib import Path

from weatherapi_collector.config import DB_SETTINGS
from weatherapi_collector.db_client import Base
from weatherapi_collector.depends.db_depends import get_db_engine

from loguru import logger as log
from shared.db import create_base_metadata

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

    log.info(f"Initializing database at {engine.url}")
    try:
        create_base_metadata(base=Base, engine=engine)
        log.info(f"Database initialized")
    except Exception as e:
        log.error(f"Failed to initialize database: {e}")
        raise
