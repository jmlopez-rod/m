import logging

from m.core import io as mio

from .formatters import CiFormatter, JsonFormatter
from .handlers import JsonFileHandler, StdErrHandler, StdOutHandler


def logging_config(level: int | None = None, json_file: str = '') -> None:
    """Apply a configuration to the logs.

    Args:
        level: The logging level, defaults to INFO.
        json_file: Optional file name where to store each log record as json.
    """
    formatter = CiFormatter()
    stdout_handler = StdOutHandler(formatter)
    stderr_handler = StdErrHandler(formatter)
    all_handlers = [stderr_handler, stdout_handler]
    if json_file:
        json_formatter = JsonFormatter()
        all_handlers.append(JsonFileHandler(json_formatter, json_file))

    debug_logs = mio.env('DEBUG_M_LOGS', 'false') == 'true'
    default_level = logging.DEBUG if debug_logs else logging.INFO
    logging_level = level if level is not None else default_level
    logging.basicConfig(
        level=logging_level,
        handlers=all_handlers,
        force=True,
    )
