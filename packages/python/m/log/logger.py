import logging
from functools import partial
from typing import Callable, cast

from m.core.fp import Good, OneOf
from m.core.issue import Issue

from .ci_tools.types import Message

PROMPT = 35


class PromptLogger(logging.Logger):
    """Adding a prompt level to the logger."""

    def __init__(self, name, level=logging.NOTSET):
        """Override the Logger init function.

        Args:
            name: Loggers name.
            level: An optional level.
        """
        super().__init__(name, level)
        logging.addLevelName(PROMPT, 'PROMPT')

    def prompt(self, msg, *args, **kwargs) -> None:
        """Log 'msg % args' with severity 'PROMPT'.

        Args:
            msg: The message to log
            args: arguments to use in the message replacement.
            kwargs: The keywords arguments to provide extra information.
        """
        if self.isEnabledFor(PROMPT):
            self._log(PROMPT, msg, args, **kwargs)


logging.setLoggerClass(PromptLogger)


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
        self.prompt = partial(
            log_func_wrapper,
            cast(PromptLogger, self.inst).prompt,
        )
        self.error = partial(log_func_wrapper, self.inst.error)

    def open_block(
        self,
        name: str,
        description: str,
        stderr: bool = False,
    ) -> OneOf[Issue, int]:
        """Group log lines.

        Signals the formatter that the next log lines should be placed in a
        group.

        Args:
            name: The name of the block to open.
            description: Not supported.
            stderr: Force message to be displayed in stderr.

        Returns:
            A OneOf containing 0 to make it easier to call in fp for loops.
        """
        func = self.inst.error if stderr else self.inst.info
        func(
            'OPEN_BLOCK',
            extra={'open_block': (name, description)},
            stacklevel=2,
        )
        return Good(0)

    def close_block(
        self,
        name: str,
        stderr: bool = False,
    ) -> OneOf[Issue, int]:
        """Close a group log lines.

        Signals the formatter that the current group of lines should end.

        Args:
            name: The name of the block to close.
            stderr: Force message to be displayed in stderr.

        Returns:
            A OneOf containing 0 to make it easier to call in fp for loops.
        """
        func = self.inst.error if stderr else self.inst.info
        func(
            'CLOSE_BLOCK',
            extra={'close_block': name},
            stacklevel=2,
        )
        return Good(0)

    def error_block(
        self,
        msg: str | Message,
        context: dict | Issue,
    ) -> OneOf[Issue, int]:
        """Display an error block.

        Args:
            msg: The error message to display.
            context: The dict/Issue to display in a block.

        Returns:
            A OneOf containing 0 to make it easier to call in fp for loops.
        """
        self.error(msg)
        self.open_block('error', '', stderr=True)
        self.error('', context)
        self.close_block('error', stderr=True)
        return Good(0)

    def waning_block(
        self,
        msg: str | Message,
        context: dict | Issue,
    ) -> OneOf[Issue, int]:
        """Display a warning block.

        Args:
            msg: The warning message to display.
            context: The dict/Issue to display in a block.

        Returns:
            A OneOf containing 0 to make it easier to call in fp for loops.
        """
        self.warning(msg)
        self.open_block('warning', '', stderr=True)
        self.warning('', context)
        self.close_block('warning', stderr=True)
        return Good(0)
