from __future__ import annotations

import logging
import os
import sys

from loguru import logger
from uvicorn import Config, Server

## Get LOG_LEVEL variable from env. Default to "INFO"
LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO"))
## Enable JSON logging if JSON_LOGS env exists and is True
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False


class InterceptHandler(logging.Handler):
    def emit(self, record):
        ## get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        ## find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_uvicorn_logging(
    colorize: bool = True,
    fmt: str = "<green>[{time:YYYY-MM-DD_HH:mm:ss}] | <level>[{level}]</level> | <level>[{name}:{line}}]</level> :: {message}",
    level: str = LOG_LEVEL,
):
    logger.configure(
        handlers=[
            {
                "sink": sys.stderr,
                "format": fmt,
                "colorize": colorize,
                "level": level,
            }
        ]
    )

    intercept_handler = InterceptHandler()

    ## level=NOTSET - loguru controls actual level
    logging.basicConfig(handlers=[intercept_handler], level=logging.NOTSET)

    for name in logging.root.manager.loggerDict.keys():
        _logger = logging.getLogger(name)
        if _logger.name.startswith("gunicorn"):
            _logger.handlers = [intercept_handler]
        else:
            ## By default uvicorn.access has a handler and doesn't propagate
            #  (uvicorn.access controls INFO messages on requests)
            _logger.propagate = True
            _logger.handlers = []
