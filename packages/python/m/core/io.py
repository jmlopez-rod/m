import os
import sys
from abc import ABC
from typing import Optional, Type


def env(name: str, def_val='') -> str:
    """Access an environment variable. Return empty string if not defined."""
    return os.environ.get(name, def_val)


def print_problem(msg):
    """Display an error message."""
    print(f'error: {msg}')


def error_block(msg):
    """Display an error block."""
    print(msg)


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

    @staticmethod
    def warn(
        description: str,
        file: Optional[str] = None,
        line: Optional[str] = None,
        col: Optional[str] = None
    ) -> None:
        """Print an warning message."""
        parts = [x for x in [file, line, col] if x]
        loc = ':'.join(parts)
        info = f'[{loc}]' if loc else ''
        print(f'warn{info}: {description}', file=sys.stderr)


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
        print(f'::error{info}::{description}', file=sys.stderr)

    @staticmethod
    def warn(
        description: str,
        file: Optional[str] = None,
        line: Optional[str] = None,
        col: Optional[str] = None
    ) -> None:
        """Print a warning message.

        https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-a-warning-message
        """  # noqa
        loc = f'file={file},line={line},col={col}' if file else ''
        info = f' {loc}' if loc else ''
        print(f'::warning{info}::{description}', file=sys.stderr)


class Teamcity(CITool):
    """Collection of methods used to communicate with Teamcity."""

    @staticmethod
    def escape_msg(msg):
        """Escapes certain characters so that Teamcity may be able to print
        correctly. See:

        https://www.jetbrains.com/help/teamcity/build-script-interaction-with-teamcity.html#BuildScriptInteractionwithTeamCity-Escapedvalues
        """  # noqa
        return msg \
            .replace('|', '||') \
            .replace("'", "|'") \
            .replace('[', '|[') \
            .replace(']', '|]') \
            .replace('\n', '|n')

    @staticmethod
    def open_block(name: str, description: str) -> None:
        """Prints a command for teamcity to begin a new block where subsequent
        output will be bundled under. See:

        https://www.jetbrains.com/help/teamcity/build-script-interaction-with-teamcity.html#BuildScriptInteractionwithTeamCity-BlocksofServiceMessages
        """  # noqa
        desc = Teamcity.escape_msg(description)
        print(f"##teamcity[blockOpened name='{name}' description='{desc}']")

    @staticmethod
    def close_block(name: str) -> None:
        """Closes a previously defined block. See `open_block`. """
        print(f"##teamcity[blockClosed name='{name}']")

    @staticmethod
    def error(
        description: str,
        file: Optional[str] = None,
        line: Optional[str] = None,
        col: Optional[str] = None
    ) -> None:
        """Print a message to teamcity so that the build may abort."""
        parts = [x for x in [file, line, col] if x]
        loc = ':'.join(parts)
        info = f'[{loc}]: ' if loc else ''
        desc = Teamcity.escape_msg(f'{info}{description}' or '')
        print(
            f"##teamcity[buildProblem description='{desc}']",
            file=sys.stderr
        )

    @staticmethod
    def warn(
        description: str,
        file: Optional[str] = None,
        line: Optional[str] = None,
        col: Optional[str] = None
    ) -> None:
        """Print a warning message to teamcity."""
        parts = [x for x in [file, line, col] if x]
        loc = ':'.join(parts)
        info = f'[{loc}]: ' if loc else ''
        desc = Teamcity.escape_msg(f'{info}{description}' or '')
        print(
            f"##teamcity[message status='WARNING' text='{desc}']",
            file=sys.stderr
        )


def get_ci_tool() -> Type[CITool]:
    """Return the current CI Tool based on the environment variables."""
    if env('GITHUB_ACTIONS'):
        return GithubActions
    if env('TC') or env('TEAMCITY'):
        return Teamcity
    return CITool


CiTool = get_ci_tool()
