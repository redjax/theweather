from __future__ import annotations

import argparse
import logging
import typing as t

from api_server.config import UVICORN_SETTINGS, LOGGING_SETTINGS
from shared.setup import setup_loguru_logging

from loguru import logger as log
from pydantic import BaseModel, Field
import uvicorn

__all__ = [
    "UvicornCustomServer",
    "UvicornSettings",
    "initialize_custom_server",
    "run_uvicorn_server",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TheWeather API server launch script.")

    parser.add_argument(
        "--app",
        type=str,
        default=UVICORN_SETTINGS.get("APP", "api_server.main:app"),
        help="Path to the FastAPI `App()` instance, i.e. `main:app`.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=UVICORN_SETTINGS.get("HOST", "127.0.0.1"),
        help="Host IP to serve API on. (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=UVICORN_SETTINGS.get("PORT", 8000),
        help="Port to serve API on. (default: 8000)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=UVICORN_SETTINGS.get("WORKERS", 1),
        help="Number of worker processes. (default: 1)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=UVICORN_SETTINGS.get("RELOAD", False),
        help="Reload on file changes. (default: False)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=UVICORN_SETTINGS.get("DEBUG", False),
        help="Enable debug mode. (default: False)",
    )
    parser.add_argument(
        "--log-level",
        default=UVICORN_SETTINGS.get("LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level. (default: INFO)",
    )

    args = parser.parse_args()

    return args


class UvicornCustomServer(BaseModel):
    """Customize a Uvicorn server by passing a dict to UvicornCustomServer.parse_obj(dict).

    Run server with instance's .run_server(). This function
    builds a Uvicorn server with the config on the instance,
    then runs it.
    """

    app: str = "api_server.main:app"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    root_path: str = "/"
    reload: bool = False

    def run_server(self) -> None:
        uvicorn.run(
            app=self.app,
            host=self.host,
            port=self.port,
            workers=self.workers,
            reload=self.reload,
            root_path=self.root_path,
        )


class UvicornSettings(BaseModel):
    """Store configuration for the Uvicorn server.

    Params:
        app (str): Path to the FastAPI `App()` instance, i.e. `main:app`.
        host (str): Host address/FQDN for the server.
        port (int): Port the server should run on.
        workers (int): Number of worker processes.
        root_path (str): The server's root path/endpoint.
        reload (bool): If `True`, server will reload when changes are detected.
        log_level (str): The log level for the Uvicorn server.
    """

    app: str = Field(default=UVICORN_SETTINGS.get("APP", "main:app"))
    host: str = Field(default=UVICORN_SETTINGS.get("HOST", "127.0.0.1"))
    port: int = Field(default=UVICORN_SETTINGS.get("PORT", 8000))
    workers: int = Field(default=UVICORN_SETTINGS.get("WORKERS", 1))
    root_path: str = Field(default=UVICORN_SETTINGS.get("ROOT_PATH", "/"))
    reload: bool = Field(default=UVICORN_SETTINGS.get("RELOAD", False))
    log_level: str = Field(default=UVICORN_SETTINGS.get("LOG_LEVEL", "INFO"))


def initialize_custom_server(
    uvicorn_settings: UvicornSettings,
    uvicorn_log_level: str = "WARNING",
) -> UvicornCustomServer:
    match uvicorn_log_level.upper():
        case "DEBUG":
            _log_level = logging.DEBUG
        case "INFO":
            _log_level = logging.INFO
        case "WARNING":
            _log_level = logging.WARNING
        case "ERROR":
            _log_level = logging.ERROR
        case "CRITICAL":
            _log_level = logging.CRITICAL
        case _:
            log.critical(
                f"Invalid logging levelname: '{uvicorn_log_level}'. Must be one of: [DEBUG, INFO, WARNING, ERROR, CRITICAL]"
            )

            raise ValueError(f"Invalid logging levelname: '{uvicorn_log_level}")

    log.debug(f"Override uvicorn's logging level, set to: '{uvicorn_log_level}'.")
    ## Set Uvicorn's log level
    logging.getLogger(name="uvicorn").setLevel(level=_log_level)

    log.debug(f"Building UvicornCustomServer")

    try:
        ## Initialize server object
        UVICORN_SERVER: UvicornCustomServer = UvicornCustomServer(
            app=uvicorn_settings.app,
            host=uvicorn_settings.host,
            port=uvicorn_settings.port,
            root_path=uvicorn_settings.root_path,
            reload=uvicorn_settings.reload,
        )

        return UVICORN_SERVER
    except Exception as exc:
        msg = Exception(
            f"Unhandled excpetion building UvicornCustomServer. Details: {exc}"
        )
        log.critical(msg)

        raise exc


def run_uvicorn_server(uvicorn_server: UvicornCustomServer):
    if not uvicorn_server:
        raise ValueError("Missing UvicornCustomServer instance.")

    log.info(f"Starting Uvicorn server")
    try:
        uvicorn_server.run_server()
    except Exception as exc:
        msg = Exception(f"Unhandled exception starting Uvicorn server. Details: {exc}")
        log.critical(msg)

        raise exc


if __name__ == "__main__":
    args = parse_args()

    setup_loguru_logging(log_level=args.log_level.upper())
    # setup.setup_database()

    uvicorn_settings = UvicornSettings(
        app=args.app,
        host=args.host,
        port=args.port,
        workers=args.workers,
        reload=args.reload,
        log_level=args.log_level,
    )
    log.debug(f"Uvicorn settings object: {uvicorn_settings}")

    UVICORN_SERVER: UvicornCustomServer = initialize_custom_server(
        uvicorn_settings=uvicorn_settings
    )

    log.info(f"Starting Uvicorn server")
    try:
        UVICORN_SERVER.run_server()
    except Exception as exc:
        msg = Exception(f"Unhandled exception starting Uvicorn server. Details: {exc}")
        log.critical(msg)

        raise exc
