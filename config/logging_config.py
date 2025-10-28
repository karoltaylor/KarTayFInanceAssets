"""Logging configuration for the application."""
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from .settings import settings


def setup_logging():
    """Configure application logging with file and console handlers."""
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger("finance_assets")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        settings.log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "finance_assets"):
    """Get a logger instance which is a child of the app logger.

    Using a child logger ensures all logs propagate to the configured
    handlers on the main application logger (file + console).
    """
    app_logger = logging.getLogger("finance_assets")
    if name == "finance_assets" or not name:
        return app_logger
    return app_logger.getChild(name)

