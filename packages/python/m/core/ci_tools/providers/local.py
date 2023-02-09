from m.core import Issue, OneOf, one_of

from m import git

from ..misc import default_formatter
from ..types import EnvVars, Message, ProviderModule


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


def open_block(name: str, description: str) -> str:
    """Display the name and description of a block.

    Local environments do not support blocks like Github and Teamcity.

    Args:
        name: Name of the block.
        description: The block description.
        stream: Defaults to sys.stdout.
    """
    desc = f' {description}' if description else ''
    return f'{name}:{desc}'


def close_block(name: str) -> str:
    """Display an empty line to denote the end of a block.

    Args:
        name: The name of the block to close.
        stream: Defaults to sys.stdout.
    """
    # pylint: disable=unused-argument
    return ''


def error(msg: Message, message: str, postfix: str) -> str:
    """Print an error message.

    Supports file, line and col properties of Message.

    Args:
        msg: The message to display.
    """
    return default_formatter(msg, message, postfix)


def warn(msg: Message, message: str, postfix: str) -> str:
    """Print an warning message.

    Supports file, line and col properties of Message.

    Args:
        msg: The message to display.
    """
    return default_formatter(msg, message, postfix)


tool = ProviderModule(
    ci=False,
    env_vars=env_vars,
    open_block=open_block,
    close_block=close_block,
    error=error,
    warn=warn,
)
