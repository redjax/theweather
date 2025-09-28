import asyncio

from shared.setup import setup_loguru_logging
from temporal_scheduler.weatherapi import scripts

from loguru import logger as log

if __name__ == "__main__":
    setup_loguru_logging()
    log.debug("DEBUG logging enabled")

    log.info("Running WeatherAPI workflows")

    try:
        asyncio.run(scripts.run_weatherapi_workflow())
    except Exception as e:
        log.error(f"Failed to run WeatherAPI workflow: ({type(e).__name__}) {e}")
