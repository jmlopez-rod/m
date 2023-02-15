import logging

from .formatters import CiFormatter, JsonFormatter
from .handlers import JsonFileHandler, StdErrHandler, StdOutHandler


def logging_config(json_file: str = '') -> None:
    """Apply a configuration to the logs.

    Args:
        json_file: Optional file name where to store each log record as json.
    """
    formatter = CiFormatter()
    stdout_handler = StdOutHandler(formatter)
    stderr_handler = StdErrHandler(formatter)
    all_handlers = [stderr_handler, stdout_handler]
    if json_file:
        json_formatter = JsonFormatter()
        all_handlers.append(JsonFileHandler(json_formatter, json_file))

    logging.basicConfig(
        level=logging.NOTSET,
        handlers=all_handlers,
        force=True,
    )
