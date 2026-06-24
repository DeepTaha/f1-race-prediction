"""
Shared utilities: logging factory and timing decorator.
"""

import logging
import time
from functools import wraps
from typing import Callable, Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Return a consistently formatted logger for the given module name."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    if level:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    return logger


def timed(logger: Optional[logging.Logger] = None) -> Callable:
    """Decorator that logs how long a function takes to run."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            log = logger or get_logger(func.__module__)
            t0 = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - t0
            log.info("%s finished in %.2fs", func.__name__, elapsed)
            return result
        return wrapper
    return decorator
