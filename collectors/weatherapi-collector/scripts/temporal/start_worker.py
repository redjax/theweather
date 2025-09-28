from shared.setup import setup_loguru_logging

from weatherapi_collector.temporal_worker import start_worker

from loguru import logger as log

if __name__ == "__main__":
    setup_loguru_logging()
    log.debug("DEBUG logging enabled")

    log.info("Starting Temporal worker")
    start_worker()
