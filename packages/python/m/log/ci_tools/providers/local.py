import logging

from m.core import Issue, OneOf, one_of
from m.log.misc import default_record_fmt, format_context, format_location

from m import git

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


def log_format(
    formatter: logging.Formatter,
    record: logging.LogRecord,
    show_traceback: bool,
    debug_python: bool,
) -> str:
    """Format a log record using the functions provided in this module.

    This function is meant to be used by a log formatter. See more info


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
        return f'>>> [{name}]: {desc}'.rstrip()

    if record_dict.get('close_block'):
        return ''

    indent = len(record.levelname) + 3
    context = format_context(record, indent, show_traceback=show_traceback)
    if not record.msg:
        return context[1:]

    ci_info = record_dict.get('ci_info', Message(msg=record.msg))
    msg_info = format_location([ci_info.file, ci_info.line, ci_info.col])
    loc = (
        format_location([record.pathname, f'{record.lineno}'], 'bold_aqua')
        if debug_python
        else ''
    )

    return default_record_fmt(
        record,
        formatter.formatTime(record, formatter.datefmt),
        f'{msg_info}{loc}',
        context,
    )


tool = ProviderModule(
    ci=False,
    env_vars=env_vars,
    formatter=log_format,
)
