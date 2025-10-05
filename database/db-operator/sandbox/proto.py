from shared.setup import setup_loguru_logging
from db_operator.config import DB_SETTINGS, LOGGING_SETTINGS
from db_operator.depends import db_depends

from loguru import logger as log

if __name__ == "__main__":
    setup_loguru_logging(log_level=LOGGING_SETTINGS.get("LEVEL"), log_file_path="logs/db_operator_prototype.log")
    log.debug("DEBUG logging enabled")
    
    log.debug(f"DB_SETTINGS: {DB_SETTINGS}")
    
    with db_depends.get_db() as session:
        log.info("DB connected")
        pass