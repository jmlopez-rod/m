import sys
from typing import TextIO

from m.core import Good, Issue, OneOf

from ..types import EnvVars, Message, ProviderModule

REPLACEMENTS = (
    ('|', '||'),
    ("'", "|'"),
    ('[', '|['),
    (']', '|]'),
    ('\n', '|n'),
)

# Do not use outside of module. This is done here to avoid
# disabling a flake8 for every ci tool method.
_print = print


def escape_msg(msg: str) -> str:
    """Escapes characters so Teamcity can print correctly.

    https://www.jetbrains.com/help/teamcity/build-script-interaction-with-teamcity.html#BuildScriptInteractionwithTeamCity-Escapedvalues
    """
    message = msg
    for target, replacement in REPLACEMENTS:
        message = message.replace(target, replacement)
    return message


def env_vars() -> OneOf[Issue, EnvVars]:
    """Read basic environment variables from Teamcity."""
    # WIP: Need to map other variables here. Not willing to do
    # at the moment since I'm using Github.
    return Good(EnvVars(ci_env=True))


def open_block(
    name: str,
    description: str,
    stream: TextIO | None = None,
) -> None:
    """Display the name and description of a block.

    https://www.jetbrains.com/help/teamcity/build-script-interaction-with-teamcity.html#BuildScriptInteractionwithTeamCity-BlocksofServiceMessages

    Args:
        name: Name of the block.
        description: The block description.
        stream: Defaults to sys.stdout.
    """
    desc = escape_msg(description)
    _print(
        f"##teamcity[blockOpened name='{name}' description='{desc}']",
        file=stream or sys.stdout,
    )


def close_block(name: str, stream: TextIO | None = None) -> None:
    """Closes a previously defined block.

    Args:
        name: The name of the block to close.
        stream: Defaults to sys.stdout.
    """
    _print(f"##teamcity[blockClosed name='{name}']", file=stream or sys.stdout)


def error(msg: Message | str) -> None:
    """Print an error message.

    Doing so will make Teamcity abort the job.
    Supports file, line and col properties of Message.

    Args:
        msg: The message to display.
    """
    if isinstance(msg, str):
        _print(
            f"##teamcity[buildProblem description='{msg}']",
            file=sys.stderr,
        )
        return
    stream = msg.stream or sys.stderr
    parts = [x for x in [msg.file, msg.line, msg.col] if x]
    loc = ':'.join(parts)
    info = f'[{loc}]: ' if loc else ''
    desc = escape_msg(f'{info}{msg.message}' or '')
    _print(
        f"##teamcity[buildProblem description='{desc}']",
        file=stream,
    )


def warn(msg: Message | str) -> None:
    """Print an warning message to Teamcity.

    Supports file, line and col properties of Message.

    Args:
        msg: The message to display.
    """
    if isinstance(msg, str):
        print(
            f"##teamcity[message status='WARNING' text='{msg}']",
            file=sys.stderr,
        )
        return
    stream = msg.stream or sys.stderr
    parts = [x for x in [msg.file, msg.line, msg.col] if x]
    loc = ':'.join(parts)
    info = f'[{loc}]: ' if loc else ''
    desc = escape_msg(f'{info}{msg.message}' or '')
    _print(
        f"##teamcity[message status='WARNING' text='{desc}']",
        file=stream,
    )


tool = ProviderModule(
    env_vars=env_vars,
    open_block=open_block,
    close_block=close_block,
    error=error,
    warn=warn,
)
