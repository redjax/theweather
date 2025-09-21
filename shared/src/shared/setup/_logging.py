import sys
from loguru import logger
from typing import Optional
from shared.config import SHARED_SETTINGS
from pathlib import Path

__all__ = ["setup_loguru_logging"]


def setup_loguru_logging(
    log_level: Optional[str] = None,
    log_file_path: Optional[str] = None,
) -> None:
    # Remove all existing handlers first
    logger.remove()

    # Determine effective log level from param or config
    effective_level = log_level or SHARED_SETTINGS.get("LOGGING", {}).get(
        "LOG_LEVEL", "INFO"
    )

    # Prepare console format: detailed for debug, simple otherwise
    console_format = (
        "<yellow>[{time:YYYY-MM-DD HH:mm:ss}]</yellow> | <level>{level:<8}</level> | "
        "<cyan>{file}</cyan>:<cyan>{line}</cyan> :: <level>{message}</level>"
        if effective_level.upper() == "DEBUG"
        else "<yellow>[{time:YYYY-MM-DD HH:mm:ss}]</yellow> | <level>{level:<8}</level> :: <level>{message}</level>"
    )

    # Add console sink logging to sys.stderr to respect log levels properly
    logger.add(
        sys.stderr,
        level=effective_level.upper(),
        format=console_format,
        colorize=True,
    )

    # Optional file logging for debug with detailed context
    if log_file_path:
        if not Path(log_file_path).exists():
            Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)

        file_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | "
            "<cyan>{file}</cyan>:<cyan>{line}</cyan> - {message}"
        )

        logger.add(
            log_file_path,
            level="DEBUG",
            format=file_format,
            rotation="10 MB",
            retention="10 days",
            compression="zip",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )
