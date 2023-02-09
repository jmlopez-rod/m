from m.core import Good, Issue, OneOf

from ..misc import default_formatter
from ..types import EnvVars, Message, ProviderModule

REPLACEMENTS = (
    ('|', '||'),
    ("'", "|'"),
    ('[', '|['),
    (']', '|]'),
    ('\n', '|n'),
)


def escape_msg(msg: str) -> str:
    """Escapes characters so Teamcity can print correctly.

    https://www.jetbrains.com/help/teamcity/build-script-interaction-with-teamcity.html#BuildScriptInteractionwithTeamCity-Escapedvalues

    Args:
        msg: The message to process.

    Returns:
        A message that can be provided to Teamcity.
    """
    message = msg
    for target, replacement in REPLACEMENTS:
        message = message.replace(target, replacement)
    return message


def _escape(name: str, description: str) -> str:
    desc = escape_msg(description)
    return f"{name}='{desc}'"


def _tc(cmd: str, postfix, **kwargs) -> str:
    key_items = ' '.join(
        [_escape(name, desc) for name, desc in kwargs.items()],
    ).strip()
    return f'##teamcity[{cmd} {key_items}]{postfix}'


def env_vars() -> OneOf[Issue, EnvVars]:
    """Read basic environment variables from Teamcity.

    Returns:
        An EnvVar instance.
    """
    # WIP: Need to map other variables here. Not willing to do
    # at the moment since I'm using Github.
    return Good(EnvVars(ci_env=True))


def open_block(name: str, description: str) -> str:
    """Display the name and description of a block.

    https://www.jetbrains.com/help/teamcity/build-script-interaction-with-teamcity.html#BuildScriptInteractionwithTeamCity-BlocksofServiceMessages

    Args:
        name: Name of the block.
        description: The block description.

    Returns:
        A formatted string.
    """
    return _tc('blockOpened', postfix='', name=name, description=description)


def close_block(name: str) -> str:
    """Close a previously defined block.

    Args:
        name: The name of the block to close.

    Returns:
        A formatted string.
    """
    return _tc('blockClosed', postfix='', name=name)


def error(_msg: Message, message: str, postfix: str) -> str:
    """Print an error message.

    Doing so will make Teamcity abort the job.
    Supports file, line and col properties of Message.

    Args:
        _msg: The message information.
        message: A formatted string that may include information from `_msg`.
        postfix: Anything that may need to be displayed after the message.

    Returns:
        A formatted string.
    """
    return _tc('buildProblem', postfix=postfix, description=message)


def warn(_msg: Message, message: str, postfix: str) -> str:
    """Print an warning message to Teamcity.

    Supports file, line and col properties of Message.

    Args:
        _msg: The message information.
        message: A formatted string that may include information from `_msg`.
        postfix: Anything that may need to be displayed after the message.

    Returns:
        A formatted string.
    """
    return _tc('message', status='WARNING', text=message, postfix=postfix)


tool = ProviderModule(
    ci=True,
    env_vars=env_vars,
    open_block=open_block,
    close_block=close_block,
    error=error,
    warn=warn,
)
