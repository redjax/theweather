from __future__ import annotations

import asyncio

from weatherapi_collector.config import TEMPORAL_SETTINGS
from weatherapi_collector.schedules.temporal import worker

from loguru import logger as log
from shared.setup import setup_loguru_logging

__all__ = ["start_worker"]


def start_worker():
    log.debug("DEBUG logging enabled")

    log.debug(f"Temporal settings: {TEMPORAL_SETTINGS}")

    log.info("Starting Temporal worker")
    try:
        asyncio.run(worker.main())
    except Exception as exc:
        log.error(f"Temporal worker exited unsuccessfuly: ({type(exc).__name__}) {exc}")
        raise
    except KeyboardInterrupt:
        log.warning("Temporal worker operation cancelled by user")
        return


if __name__ == "__main__":
    setup_loguru_logging()

    try:
        start_worker()
    except Exception as exc:
        log.error(f"Failed while running Temporal worker: ({type(exc).__name__}) {exc}")
