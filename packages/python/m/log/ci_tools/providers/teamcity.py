import logging

from m.core import Good, Issue, OneOf
from m.log.misc import format_context, format_location

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


def log_format(
    formatter: logging.Formatter,
    record: logging.LogRecord,
    show_traceback: bool,
    debug_python: bool,
) -> str:
    """Format a log record using the functions provided in this module.

    This function is meant to be used by a log formatter. See more info

    See::
        https://www.jetbrains.com/help/teamcity/build-script-interaction-with-teamcity.html#BuildScriptInteractionwithTeamCity-BlocksofServiceMessages

    Args:
        formatter: A log formatter instance.
        record: A log record.
        show_traceback: If true, display the python stack trace.
        debug_python: If true, display the location of the record's origin.

    Returns:
        A formatted string.
    """
    record_dict = record.__dict__

    open_b = record_dict.get('open_block')
    if open_b:
        name, desc = open_b
        return _tc('blockOpened', postfix='', name=name, description=desc)

    close_b = record_dict.get('close_block')
    if close_b:
        return _tc('blockClosed', postfix='', name=close_b)

    level_name = record.levelname.lower()
    is_command = level_name in {'warning', 'error'}

    indent_padding = 2 if is_command else 3
    indent = len(record.levelname) + indent_padding

    context = format_context(record, indent, show_traceback=show_traceback)

    ci_info = record_dict.get('ci_info', Message(msg=record.msg))
    msg_info = format_location([ci_info.file, ci_info.line, ci_info.col])

    loc = (
        format_location([record.pathname, f'{record.lineno}'])
        if debug_python
        else ''
    )

    msg = f'{loc} {record.msg}'.lstrip()
    if level_name == 'warning':

        return _tc(
            'message',
            status='WARNING',
            text=msg,
            postfix=context,
        )
    if level_name == 'error':
        return _tc('buildProblem', postfix=context, description=msg)

    msg = record.msg
    message = f'[{record.levelname}] {msg_info}{loc}: {msg}'
    return f'{message}{context}'


tool = ProviderModule(
    ci=True,
    env_vars=env_vars,
    formatter=log_format,
)
