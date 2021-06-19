import os
import sys
import json
from abc import ABC
from typing import Any, Optional, Type
from .fp import Good, OneOf
from .issue import Issue, issue


def env(name: str, def_val='') -> str:
    """Access an environment variable. Return empty string if not defined."""
    return os.environ.get(name, def_val)


def print_problem(msg):
    """Display an error message."""
    print(f'error: {msg}')


def error_block(msg):
    """Display an error block."""
    print(msg)


def read_json(
    filename: Optional[str],
    error_if_empty=False
) -> OneOf[Issue, Any]:
    """Return a `Good` containing the parsed contents of the json file."""
    try:
        empty = '' if error_if_empty else 'null'
        if filename is None:
            return Good(json.loads(sys.stdin.read() or empty))
        return Good(json.loads(open(filename).read() or empty))
    except Exception as ex:
        return issue(
            'failed to read json file',
            data={'filename': filename or 'SYS.STDIN'},
            cause=ex)


def parse_json(data: str, error_if_empty=False) -> OneOf[Issue, Any]:
    """Return a `Good` containing the parsed contents of the json string."""
    try:
        empty = '' if error_if_empty else 'null'
        return Good(json.loads(data or empty))
    except Exception as ex:
        return issue('failed to parse the json data', cause=ex)


class CITool(ABC):
    """Class representing a continuous integration tool. We can use this
    class static methods to display local messages."""

    @staticmethod
    def open_block(name: str, description: str) -> None:
        """Define how a block is opened."""
        print(f'{name}: {description}')

    @staticmethod
    def close_block(_name: str) -> None:
        """Define how a block is closed."""
        ...

    @staticmethod
    def error(
        description: str,
        file: Optional[str] = None,
        line: Optional[str] = None,
        col: Optional[str] = None
    ) -> None:
        """Print an error message."""
        parts = [x for x in [file, line, col] if x]
        loc = ':'.join(parts)
        info = f'[{loc}]' if loc else ''
        print(f'error{info}: {description}', file=sys.stderr)


class GithubActions(CITool):
    """Collection of methods used to communicate with Github."""

    @staticmethod
    def open_block(name: str, _description: str) -> None:
        """Group log lines. There is no description field and it does not
        support nesting.

        https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#grouping-log-lines
        """
        print(f'::group::{name}')

    @staticmethod
    def close_block(_name: str) -> None:
        """Since Github Actions does not support nesting blocks, all this does
        is close the current block."""
        print('::endgroup::')

    @staticmethod
    def error(
        description: str,
        file: Optional[str] = None,
        line: Optional[str] = None,
        col: Optional[str] = None
    ) -> None:
        """Print an error message.

        https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-an-error-message
        """
        loc = f'file={file},line={line},col={col}' if file else ''
        info = f' {loc}' if loc else ''
        print(f'::error{info}:: {description}', file=sys.stderr)



def get_ci_tool() -> Type[CITool]:
    """Return the current CI Tool based on the environment variables."""
    if env('GITHUB_ACTIONS'):
        return GithubActions
    return CITool


CiTool = get_ci_tool()
