"""
Logger Configuration Module.

This module provides a centralized logging setup for the FastAPI application.
It configures logging to both the console (for development) and a rotating file
(for production monitoring), ensuring all parts of the app log consistently.
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler


os.makedirs("logs", exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a configured logger instance.

    Logs DEBUG and above to console.
    Logs WARNING and above to logs/app.log with daily rotation.
    Keeps 90 days of log history.

    Args:
        name: the module name, pass __name__ from the calling module.

    Returns:
        A configured Logger instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    file_handler = TimedRotatingFileHandler(
        filename="logs/app.log",
        when="midnight",
        interval=1,
        backupCount=90,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y-%m-%d"

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger