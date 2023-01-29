import sys
from typing import TextIO

from m.core import Issue, OneOf, one_of

from m import git

from ..types import EnvVars, Message, ProviderModule

# Do not use outside of module. This is done here to avoid
# disabling a flake8 for every ci tool method.
_print = print


def env_vars() -> OneOf[Issue, EnvVars]:
    """Obtain basic environment variables in a local environment.

    Returns:
        An `EnvVars` instance if successful.
    """
    return one_of(
        lambda: [
            EnvVars(
                git_branch=git_branch,
                git_sha=git_sha,
            )
            for git_branch in git.get_branch()
            for git_sha in git.get_current_commit_sha()
        ],
    )


def open_block(
    name: str,
    description: str,
    stream: TextIO | None = None,
) -> None:
    """Display the name and description of a block.

    Local environments do not support blocks like Github and Teamcity.

    Args:
        name: Name of the block.
        description: The block description.
        stream: Defaults to sys.stdout.
    """
    desc = f' {description}' if description else ''
    _print(f'{name}:{desc}', file=stream or sys.stdout)


def close_block(name: str, stream: TextIO | None = None) -> None:
    """Display an empty line to denote the end of a block.

    Args:
        name: The name of the block to close.
        stream: Defaults to sys.stdout.
    """
    # pylint: disable=unused-argument
    _print('', file=stream or sys.stdout)


def error(msg: Message | str) -> None:
    """Print an error message.

    Supports file, line and col properties of Message.

    Args:
        msg: The message to display.
    """
    if isinstance(msg, str):
        _print(f'error: {msg}', file=sys.stderr)
        return
    stream = msg.stream or sys.stderr
    parts = [x for x in (msg.file, msg.line, msg.col) if x]
    loc = ':'.join(parts)
    msg_info = f'[{loc}]' if loc else ''
    _print(f'error{msg_info}: {msg.message}', file=stream or sys.stderr)


def warn(msg: Message | str) -> None:
    """Print an warning message.

    Supports file, line and col properties of Message.

    Args:
        msg: The message to display.
    """
    if isinstance(msg, str):
        _print(f'warn: {msg}', file=sys.stderr)
        return
    stream = msg.stream or sys.stderr
    parts = [x for x in (msg.file, msg.line, msg.col) if x]
    loc = ':'.join(parts)
    msg_info = f'[{loc}]' if loc else ''
    _print(f'warn{msg_info}: {msg.message}', file=stream)


tool = ProviderModule(
    env_vars=env_vars,
    open_block=open_block,
    close_block=close_block,
    error=error,
    warn=warn,
)
