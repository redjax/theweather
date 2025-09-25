from api_server.start_api import main as start_api
from loguru import logger as log

from shared.setup import setup_loguru_logging
from api_server.config import SETTINGS, DB_SETTINGS


def main():
    setup_loguru_logging(
        log_level=SETTINGS.get("LOGGING_SETTINGS", {}).get("LOG_LEVEL", "INFO")
    )
    log.debug(f"Debug logging enabled.")

    try:
        start_api()
    except KeyboardInterrupt:
        log.warning("API server stopped by user.")
        exit(0)
    except Exception as e:
        log.error(f"({type(e)}) Unexpected error running API server: {e}")
        exit(1)


if __name__ == "__main__":
    main()
