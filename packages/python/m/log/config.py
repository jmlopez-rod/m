import logging

from .formatters import CiFormatter
from .handlers import StdErrHandler, StdOutHandler


def logging_config(level: int = logging.NOTSET) -> None:
    """Apply a configuration to the logs.

    Args:
        level: The logger level to enable.
    """
    formatter = CiFormatter()
    stdout_handler = StdOutHandler(formatter)
    stderr_handler = StdErrHandler(formatter)
    logging.basicConfig(
        level=level,
        handlers=[stderr_handler, stdout_handler],
        force=True,
    )
