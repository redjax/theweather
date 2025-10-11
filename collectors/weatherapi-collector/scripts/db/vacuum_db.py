from __future__ import annotations

from loguru import logger as log
from shared.setup import setup_loguru_logging
from weatherapi_collector.config import DB_SETTINGS
from weatherapi_collector.db_client import vacuum_current_weather

if __name__ == "__main__":
    setup_loguru_logging()
    log.debug("DEBUG logging enabled")

    log.info("Starting database vacuum process")
    try:
        rows_deleted = vacuum_current_weather()
        log.info(f"Database vacuum complete. Rows deleted: {rows_deleted}")
    except Exception as exc:
        log.error(f"Error during database vacuum: {exc}")
