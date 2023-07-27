import logging
from typing import cast

from m.color import color
from m.core import Issue, OneOf
from m.core import io as mio
from m.core import issue, one_of
from m.log.misc import default_record_fmt, format_context, format_location
from pydantic import BaseModel, Field

from ..types import EnvVars, Message, ProviderModule


class GithubEnvVars(BaseModel):
    """Environment variables required when running in Github."""

    repo: str = Field('GITHUB_REPOSITORY')
    run_id: str = Field('GITHUB_RUN_ID')
    run_number: str = Field('GITHUB_RUN_NUMBER')
    github_token: str = Field('GITHUB_TOKEN')
    git_branch: str = Field('GITHUB_REF')
    git_sha: str = Field('GITHUB_SHA')
    triggered_by: str = Field('GITHUB_ACTOR')


def env_vars() -> OneOf[Issue, EnvVars]:
    """Read the environment variables from Github Actions.

    Returns:
        An `EnvVars` instance or an Issue.
    """
    server_url = 'https://github.com'
    return one_of(
        lambda: [
            EnvVars(
                **env.dict(),
                ci_env=True,
                server_url=server_url,
                run_url=run_url,
            )
            for env in mio.env_model(GithubEnvVars)
            for run_url in (
                f'{server_url}/{env.repo}/actions/runs/{env.run_id}',
            )
        ],
    ).flat_map_bad(lambda x: issue(
        'GH Actions env_vars failure', cause=cast(Issue, x),
    ))


def _gh_format(msg_type: str, msg: Message, message: str, postfix: str) -> str:
    """Format an error or warning message for Github.

    See::

        https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-an-error-message
        https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-a-warning-message

    Args:
        msg_type: either error or warnings.
        msg: A Message instance.
        message: A simple message.
        postfix: A string to print after the simple message.

    Returns:
        A formatted string.
    """
    file_entry = f'file={msg.file}' if msg.file else ''
    line_entry = f'line={msg.line}' if msg.line else ''
    col_entry = f'col={msg.col}' if msg.col else ''
    parts = [x for x in (file_entry, line_entry, col_entry) if x]
    loc = ','.join(parts)
    msg_info = f' {loc}' if loc else ''
    return f'::{msg_type}{msg_info}::{message}{postfix}'


def _format_block(name, desc) -> str:
    with_desc = f'{{gray}} - {desc}' if desc else ''
    return color(
        f'::group::{{bold_purple}}{name}',
        with_desc,
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
        return _format_block(*open_b)

    if record_dict.get('close_block'):
        return '::endgroup::'

    is_command = record.levelname in {'WARNING', 'ERROR'}

    indent_padding = 2 if is_command else 3
    indent = len(record.levelname) + indent_padding

    ci_info = record_dict.get('ci_info', Message(msg=record.msg))
    context = format_context(record, indent, show_traceback=show_traceback)
    if not record.msg:
        return context[1:]

    loc = (
        format_location([record.pathname, f'{record.lineno}'])
        if debug_python
        else ''
    )
    if is_command:
        msg = f'{loc} {record.msg}'.lstrip()
        return _gh_format(record.levelname.lower(), ci_info, msg, context)
    return default_record_fmt(
        record,
        formatter.formatTime(record, formatter.datefmt),
        loc,
        context,
    )


tool = ProviderModule(
    ci=True,
    env_vars=env_vars,
    formatter=log_format,
)
