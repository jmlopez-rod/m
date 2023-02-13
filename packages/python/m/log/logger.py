import logging
from functools import partial
from typing import Callable

from m.core.fp import Good, OneOf
from m.core.issue import Issue

from .ci_tools.types import Message


def log_func_wrapper(
    func: Callable,
    msg: str | Message,
    context: dict | Issue | None = None,
    exit_code: int = 0,
) -> OneOf[Issue, int]:
    """Call a logger function with a message and log data.

    Args:
        func: A logger function (logger.info)
        msg: A string or Message containing information about the log.
        context: Data describing the log entry.
        exit_code: Used in cli context to force an exit. Default to 0.

    Returns:
        A OneOf containing 0 to make it easier to call in fp for loops.
        May be overwritten when signaling an error.
    """
    if isinstance(msg, str):
        func(msg, extra={'context': context}, stacklevel=2)
    else:
        func(
            msg.msg,
            extra={'context': context, 'ci_info': msg},
            stacklevel=2,
        )
    return Good(exit_code)


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

    def open_block(self, name: str, description: str) -> OneOf[Issue, int]:
        """Group log lines.

        Signals the formatter that the next log lines should be placed in a
        group.

        Args:
            name: The name of the block to open.
            description: Not supported.

        Returns:
            A OneOf containing 0 to make it easier to call in fp for loops.
        """
        self.inst.info(
            'OPEN_BLOCK',
            extra={'open_block': (name, description)},
            stacklevel=2,
        )
        return Good(0)

    def close_block(self, name: str) -> OneOf[Issue, int]:
        """Close a group log lines.

        Signals the formatter that the current group of lines should end.

        Args:
            name: The name of the block to close.

        Returns:
            A OneOf containing 0 to make it easier to call in fp for loops.
        """
        self.inst.info(
            'CLOSE_BLOCK',
            extra={'close_block': name},
            stacklevel=2,
        )
        return Good(0)
