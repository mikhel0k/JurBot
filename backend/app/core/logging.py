import logging
import sys

from settings import settings

_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
_handler = logging.StreamHandler(sys.stdout)
_handler.setFormatter(logging.Formatter("%(levelname)s | %(name)s | %(message)s"))

_root = logging.getLogger()
_root.setLevel(_level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
