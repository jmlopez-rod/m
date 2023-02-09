import json
import logging
import textwrap
from functools import partial
from typing import Any, Callable

from .ci_tools import Message, default_formatter, get_ci_tool
from .fp import Good, OneOf
from .issue import Issue

LogData = dict[str, Any]


def log_func_wrapper(
    func: Callable,
    msg: str | Message,
    context: LogData | None = None,
) -> OneOf[Issue, int]:
    """Call a logger function with a message and log data.

    Args:
        func: A logger function (logger.info)
        msg: A string or Message containing information about the log.
        context: Data describing the log entry.

    Returns:
        A OneOf containing 0 to make it easier to call in fp for loops.
    """
    if isinstance(msg, str):
        func(msg, extra={'context': context}, stacklevel=2)
    else:
        func(
            msg.msg,
            extra={'context': context, 'ci_info': msg},
            stacklevel=2,
        )
    return Good(0)


class Logger:
    """Wrapper for python Logger to enable inserting logs in fp loops.

    This is also so that we may attach context data for a message.

    We can access the actual logger by using `inst`.
    """

    def __init__(self, name: str):
        """Initialize the Logger.

        Args:
            name: The name of a logger.
        """
        self.inst = logging.getLogger(name)
        self.debug = partial(log_func_wrapper, self.inst.debug)
        self.info = partial(log_func_wrapper, self.inst.info)  # noqa: WPS110
        self.warning = partial(log_func_wrapper, self.inst.warning)
        self.error = partial(log_func_wrapper, self.inst.error)


def indent_payload(
    indent: int,
    payload: dict,
    prepend_new_line: bool = True,
) -> str:
    """Stringify a dictionary as JSON and indent it.

    Args:
        indent: The number of spaces to indent.
        payload: The data to stringify and indent.
        prepend_new_line: Prepend a new line to the payload if `True`.

    Returns:
        An indented payload.
    """
    json_dict = json.dumps(payload, indent=2)
    indented_payload = textwrap.indent(json_dict, ' ' * indent)
    return f'\n{indented_payload}' if prepend_new_line else indented_payload


class StartsWithFilter(logging.Filter):
    """Filter messages from logs that have a name starting with a string."""

    def __init__(self, start_str: str):
        """Initialize a filter.

        Args:
            start_str: The
        """
        super().__init__()
        self.start_str = start_str

    def filter(self, record: logging.LogRecord) -> bool:
        """Only loggers of name starting with start_str will display.

        Args:
            record: A logging record instance.

        Returns:
            True if the logger name starts with `self.start_str`.
        """
        return record.name.startswith(self.start_str)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        record_dict = record.__dict__
        context = record_dict.get('context')
        ci_info = record_dict.get('ci_info', Message(msg=record.msg))
        replacements = {
            **record_dict,
            **ci_info.dict(),
            'asctime': self.formatTime(record, self.datefmt),
            'context': context,
        }
        replacements.pop('ci_info', '')
        sanitized = {
            key: non_empty
            for key, non_empty in replacements.items()
            if non_empty
        }
        return json.dumps(sanitized)


class MFormatter(logging.Formatter):
    """A formatter that takes into account a CI environment.

    We can still use
    """

    def __init__(
        self,
        mapping: dict[str, Callable[[str, dict], str]] | None = None,
        datefmt: str = '%I:%M:%S %p - %b %d, %Y',
        msg_fmt: str = '%(levelname)s%(asctime)s%(ci_info)s: %(msg)s',
        postfix_fmt: str = '%(context)s',
    ):
        super().__init__(datefmt=datefmt)
        mapping_update = mapping or {}
        self.mapping = {
            'levelname': lambda v, r: f'[{v}] ' if v else '',
            'asctime': lambda v, _: f'[{v}]',
            'ci_info': lambda _, r: ('[{file}:{line}:{col}]'.format(**r) if r['file'] else ''),
            **mapping_update,
        }
        self.msg_fmt = msg_fmt
        self.postfix_fmt = postfix_fmt
        self.ci_tool = get_ci_tool()

    def format(self, record):
        format_func = {
            logging.WARNING: self.ci_tool.warn,
            logging.ERROR: self.ci_tool.error,
        }.get(record.levelno, default_formatter)
        show_level = format_func is default_formatter or not self.ci_tool.ci

        indent_padding = 2 if self.ci_tool.ci else 3
        indent = len(record.levelname) + indent_padding

        record_dict = record.__dict__
        context = record_dict.get('context')
        ci_info = record_dict.get('ci_info', Message(msg=record.msg))
        replacements = {
            **record_dict,
            **ci_info.dict(),
            'asctime': self.formatTime(record, self.datefmt),
            'levelname': record.levelname if show_level else '',
            'context': indent_payload(indent, context) if context else '',
        }

        # Remove None
        for key, str_val in replacements.items():
            replacements[key] = str_val or ''

        # Create new keys
        for mapping_key, map_func in self.mapping.items():
            replacements[mapping_key] = map_func(
                replacements.get(mapping_key, ''),
                replacements,
            )

        ci_msg = self.msg_fmt % replacements
        ci_postfix = self.postfix_fmt % replacements
        return format_func(ci_info, ci_msg, ci_postfix)


def logging_config(level: int, filters: list[logging.Filter]) -> None:
    """Apply a configuration to the logs.

    Args:
        level: The logger level to enable.
        filters: An array of filters to apply to all the loggers.
    """
    logging.basicConfig(level=level)

    test_formatter = MFormatter()
    # test_formatter = JsonFormatter()
    if filters:
        for logger_handler in logging.root.handlers:
            for filter_inst in filters:
                logger_handler.addFilter(filter_inst)
            logger_handler.setFormatter(test_formatter)

    for logger_handler in logging.root.handlers:
        logger_handler.setFormatter(test_formatter)
