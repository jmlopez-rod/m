import sys
from typing import cast

from m.core import Issue, OneOf, issue, one_of
from m.core.io import renv_vars

from ..types import EnvVars, Message, ProviderModule


def env_vars() -> OneOf[Issue, EnvVars]:
    """Read the environment variables from Github Actions."""
    res = EnvVars(
        ci_env=True,
        server_url='https://github.com',
    )
    return one_of(
        lambda: [
            res
            for [
                repo,
                res.run_id,
                res.run_number,
                res.github_token,
                res.git_branch,
                res.git_sha,
                res.triggered_by,
            ] in renv_vars([
                'GITHUB_REPOSITORY',
                'GITHUB_RUN_ID',
                'GITHUB_RUN_NUMBER',
                'GITHUB_TOKEN',
                'GITHUB_REF',
                'GITHUB_SHA',
                'GITHUB_ACTOR',
            ])
            for res.run_url in [
                f'{res.server_url}/{repo}/actions/runs/{res.run_id}',
            ]
        ],
    ).flat_map_bad(lambda x: issue(
        'GH Actions env_vars failure', cause=cast(Issue, x),
    ))


def open_block(name: str, _description: str) -> None:
    """Group log lines.

    There is no description field and it does not support nesting.

    https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#grouping-log-lines

    Args:
        name: The name of the block to open.
        _description: Not supported.
    """
    print(f'::group::{name}')


def close_block(_name: str) -> None:
    """Close the current block.

    Github Actions does not support nesting blocks, all this does is close
    the current block.

    Args:
        _name: Has no effect.
    """
    print('::endgroup::')


def error(msg: Message) -> None:
    """Print an error message.

    https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-an-error-message

    Args:
        msg: The message to display.
    """
    stream = msg.stream or sys.stderr
    file_entry = f'file={msg.file}' if msg.file else ''
    line_entry = f'line={msg.line}' if msg.line else ''
    col_entry = f'col={msg.col}' if msg.col else ''
    parts = [x for x in (file_entry, line_entry, col_entry) if x]
    loc = ','.join(parts)
    info = f' {loc}' if loc else ''
    print(f'::error{info}::{msg.message}', file=stream)


def warn(msg: Message) -> None:
    """Print an warning message.

    https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-a-warning-message

    Args:
        msg: The message to display.
    """
    stream = msg.stream or sys.stderr
    file_entry = f'file={msg.file}' if msg.file else ''
    line_entry = f'line={msg.line}' if msg.line else ''
    col_entry = f'col={msg.col}' if msg.col else ''
    parts = [x for x in (file_entry, line_entry, col_entry) if x]
    loc = ','.join(parts)
    info = f' {loc}' if loc else ''
    print(f'::warning{info}::{msg.message}', file=stream)


tool = ProviderModule(
    env_vars=env_vars,
    open_block=open_block,
    close_block=close_block,
    error=error,
    warn=warn,
)
