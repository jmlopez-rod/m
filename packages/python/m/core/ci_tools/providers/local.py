import sys

from m.core import Issue, OneOf, one_of

from m import git

from ..types import EnvVars, Message, ProviderModule


def env_vars() -> OneOf[Issue, EnvVars]:
    """Obtain basic environment variables in a local environment."""
    res = EnvVars()
    return one_of(
        lambda: [
            res
            for res.git_branch in git.get_branch()
            for res.git_sha in git.get_current_commit_sha()
        ],
    )


def open_block(name: str, description: str) -> None:
    """Display the name and description of a block.

    Local environments do not support blocks like Github and Teamcity.

    Args:
        name: Name of the block.
        description: The block description.
    """
    print(f'{name}: {description}')


def close_block(_name: str) -> None:
    """Display an empty line to denote the end of a block.

    Args:
        _name: The name of the block to close.
    """
    print('')


def error(msg: Message) -> None:
    """Print an error message.

    Supports file, line and col properties of Message.

    Args:
        msg: The message to display.
    """
    stream = msg.stream or sys.stderr
    parts = [x for x in (msg.file, msg.line, msg.col) if x]
    loc = ':'.join(parts)
    info = f'[{loc}]' if loc else ''
    print(f'error{info}: {msg.message}', file=stream or sys.stderr)


def warn(msg: Message) -> None:
    """Print an warning message.

    Supports file, line and col properties of Message.

    Args:
        msg: The message to display.
    """
    stream = msg.stream or sys.stderr
    parts = [x for x in (msg.file, msg.line, msg.col) if x]
    loc = ':'.join(parts)
    info = f'[{loc}]' if loc else ''
    print(f'warn{info}: {msg.message}', file=stream)


tool = ProviderModule(
    env_vars=env_vars,
    open_block=open_block,
    close_block=close_block,
    error=error,
    warn=warn,
)
