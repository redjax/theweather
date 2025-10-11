from __future__ import annotations

import asyncio

from loguru import logger as log
from shared.setup import setup_loguru_logging
from weatherapi_collector.schedules.temporal import scripts

if __name__ == "__main__":
    setup_loguru_logging()
    log.debug("DEBUG logging enabled")

    asyncio.run(scripts.run_weather_workflow())
