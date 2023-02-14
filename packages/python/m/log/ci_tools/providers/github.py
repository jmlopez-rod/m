import logging
from typing import cast

from m.core import Issue, OneOf, issue, one_of
from m.core.io import env_model
from m.log.misc import format_context, format_location
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
            for env in env_model(GithubEnvVars)
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
        name, _ = open_b
        return f'::group::{name}'

    close_b = record_dict.get('close_block')
    if close_b:
        return '::endgroup::'

    level_name = record.levelname.lower()
    is_command = level_name in {'warning', 'error'}

    indent_padding = 2 if is_command else 3
    indent = len(record.levelname) + indent_padding

    ci_info = record_dict.get('ci_info', Message(msg=record.msg))
    context = format_context(record, indent, show_traceback=show_traceback)

    loc = (
        format_location([record.pathname, f'{record.lineno}'])
        if debug_python
        else ''
    )
    if is_command:
        msg = f'{loc} {record.msg}'
        return _gh_format(level_name, ci_info, msg, context)
    msg = record.msg
    asctime = formatter.formatTime(record, formatter.datefmt)
    message = f'[{record.levelname}] [{asctime}]{loc}: {msg}'
    return f'{message}{context}'


tool = ProviderModule(
    ci=True,
    env_vars=env_vars,
    formatter=log_format,
)
