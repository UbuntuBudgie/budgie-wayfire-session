"""
Logging configuration for Wayfire Bridge

By default only WARNING+ messages are emitted, so journalctl stays quiet
in production.  Pass --verbose / -v at startup (or set the environment
variable WAYFIRE_BRIDGE_VERBOSE=1) to enable DEBUG output.
"""

import logging
import os
import sys

# Root logger name used throughout the package
LOGGER_NAME = "wayfire_bridge"


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure the root package logger.

    Args:
        verbose: When True, emit DEBUG messages.  When False (default),
                 only WARNING and above reach the journal.

    Returns:
        The configured root logger for the wayfire_bridge package.
    """
    logger = logging.getLogger(LOGGER_NAME)

    # Avoid adding duplicate handlers if called more than once
    if logger.handlers:
        return logger

    level = logging.DEBUG if verbose else logging.WARNING
    logger.setLevel(level)

    # A StreamHandler writing to stderr is all we need:
    # systemd captures stderr and routes it to the journal when
    # StandardError=journal is set in the unit file.
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)

    # Include logger name and level; timestamp comes from journalctl
    fmt = logging.Formatter(
        fmt="%(name)s [%(levelname)s] %(message)s",
    )
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    return logger


def is_verbose() -> bool:
    """Return True if verbose logging has been requested via the environment."""
    return os.environ.get("WAYFIRE_BRIDGE_VERBOSE", "0").strip() not in ("", "0", "false", "no")


def get_logger(name: str = "") -> logging.Logger:
    """Return a child logger of the package root.

    Usage inside each module::

        from .logging_config import get_logger
        log = get_logger(__name__)

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        A :class:`logging.Logger` that inherits level/handlers from the
        package root logger.
    """
    if name and name != LOGGER_NAME:
        # e.g. "wayfire_bridge.bridge", "wayfire_bridge.config_manager" …
        return logging.getLogger(name)
    return logging.getLogger(LOGGER_NAME)
