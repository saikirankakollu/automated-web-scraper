"""Logger module providing a reusable, configurable logging setup."""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """Create and configure a logger with console and optional file handlers.

    The logger writes structured messages that include timestamp, log level,
    and module name.  When *log_file* is supplied a :class:`RotatingFileHandler`
    is added (max 10 MB per file, 5 backup files kept).

    Args:
        name: Unique name for the logger (typically ``__name__`` of the caller).
        log_file: Optional path to the log file.  Parent directories are
            created automatically.  If ``None`` only the console handler is
            attached.
        level: Minimum logging level (e.g. ``logging.DEBUG``).

    Returns:
        A fully configured :class:`logging.Logger` instance.

    Example::

        logger = setup_logger("my_module", log_file="logs/app.log")
        logger.info("Scraper started")
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers when the function is called more than
    # once for the same logger name (common in long-running processes).
    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler
    if log_file:
        os.makedirs(os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
