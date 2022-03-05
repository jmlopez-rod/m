import json
import math
import os
import sys
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, TextIO, Type, Union, cast

from .. import git
from . import issue, one_of
from .fp import Good, OneOf
from .issue import Issue


def format_seconds(number_of_seconds: Union[int, float]) -> str:
    """Return a string representing the number of seconds in a friendly
    format: Xd:Xh:Xm:Xs:Xms. """
    milliseconds = int(math.floor(number_of_seconds * 1000))
    _ms = milliseconds % 1000
    seconds = int(math.floor(milliseconds / 1000))
    sec = seconds % 60
    minutes = int(math.floor(seconds / 60))
    mins = minutes % 60
    hours = int(math.floor(minutes / 60))
    hrs = hours % 24
    days = int(math.floor(hours / 24))

    entries = [
        f'{days}d' if days else '',
        f'{hrs}h' if hours else '',
        f'{mins}m' if mins else '',
        f'{sec}s' if sec else '',
        f'{_ms}ms' if _ms else '',
    ]
    return ':'.join([x for x in entries if x]) or '0s'


def env(name: str, def_val='') -> str:
    """Access an environment variable.

    Return empty string if not defined.
    """
    return os.environ.get(name, def_val)


def renv(key: str) -> OneOf[Issue, str]:
    """Require an environment variable to be defined."""
    value = os.environ.get(key)
    # Value may still be an empty string, checking against None
    if value is not None:
        return Good(value)
    return issue(f'missing {key} in env')


def renv_vars(keys: List[str]) -> OneOf[Issue, List[str]]:
    """Require multiple env vars to be defined."""
    result: List[str] = []
    missing: List[str] = []
    for key in keys:
        value = os.environ.get(key)
        if value is None:
            missing.append(key)
        else:
            result.append(value)
    if missing:
        mstr = ', '.join(missing)
        return issue(f'missing [{mstr}] in env')
    return Good(result)


def read_file(filename: str) -> OneOf[Issue, str]:
    """Return a `Good` containing the contents of the file."""
    try:
        with open(filename, encoding='UTF-8') as fp:
            return Good(fp.read())
    except Exception as ex:
        return issue(
            'failed to read file',
            context={'filename': filename},
            cause=ex,
        )


def write_file(filename: str, contents: str) -> OneOf[Issue, int]:
    """Return a `Good` containing 0 if the file was written."""
    try:
        with open(filename, 'w', encoding='UTF-8') as fp:
            fp.write(contents)
        return Good(0)
    except Exception as ex:
        return issue(
            'failed to write file',
            context={'filename': filename},
            cause=ex,
        )


def _ver_str(major: int, minor: int, patch: int) -> str:
    return f'{major}.{minor}.{patch}'


def prompt_next_version(version: str, release_type: str) -> str:
    """Display the possible major, minor and patch versions and prompt the user
    to enter one of them. Return one of the versions.

    https://semver.org/
    """
    ver = version.split('-')[0]
    parts = [int(x) for x in ver.split('.')]
    patch = _ver_str(parts[0], parts[1], parts[2] + 1)
    if release_type == 'hotfix':
        return patch

    minor = _ver_str(parts[0], parts[1] + 1, 0)
    major = _ver_str(parts[0] + 1, 0, 0)
    valid = False
    options = [minor, major]
    msg = f'Current version is {version}. Enter one of the following:\n  '
    msg += '\n  '.join(options)
    result = ''
    while not valid:
        print(msg, file=sys.stderr)
        result = input('')
        if result in options:
            valid = True
    return result


def serialize(obj: Any) -> Any:
    """Return a serializable version of an object."""
    if isinstance(obj, Enum):
        return obj.value
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return f'[Non-Serializable {repr(obj)}]'


class JsonStr:
    """Base class to stringify dataclasses."""

    # pylint: disable=too-few-public-methods
    def __str__(self) -> str:
        return json.dumps(self.__dict__, default=serialize)


@dataclass
class EnvVars(JsonStr):
    """Class to store the values of the environment variables."""

    # pylint: disable=too-many-instance-attributes
    ci_env: bool = False
    github_token: str = ''
    server_url: str = ''
    run_id: str = ''
    run_number: str = ''
    run_url: str = ''
    git_branch: str = ''
    git_sha: str = ''
    triggered_by: str = ''
    triggered_by_email: str = ''
    triggered_by_user: str = ''


class CITool(ABC):
    """Class representing a continuous integration tool.

    We can use this class static methods to display local messages.
    """

    @staticmethod
    def env_vars() -> OneOf[Issue, EnvVars]:
        """Obtain basic environment variables."""
        res = EnvVars()
        return one_of(
            lambda: [
                res
                for res.git_branch in git.get_branch()
                for res.git_sha in git.get_current_commit_sha()
            ],
        )

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
        col: Optional[str] = None,
        stream: Optional[TextIO] = None,
    ) -> None:
        """Print an error message."""
        stream = stream or sys.stderr
        parts = [x for x in [file, line, col] if x]
        loc = ':'.join(parts)
        info = f'[{loc}]' if loc else ''
        print(f'error{info}: {description}', file=stream)

    @staticmethod
    def warn(
        description: str,
        file: Optional[str] = None,
        line: Optional[str] = None,
        col: Optional[str] = None,
        stream: Optional[TextIO] = None,
    ) -> None:
        """Print an warning message."""
        stream = stream or sys.stderr
        parts = [x for x in [file, line, col] if x]
        loc = ':'.join(parts)
        info = f'[{loc}]' if loc else ''
        print(f'warn{info}: {description}', file=stream)


class GithubActions(CITool):
    """Collection of methods used to communicate with Github."""

    @staticmethod
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
        col: Optional[str] = None,
        stream: Optional[TextIO] = None,
    ) -> None:
        """Print an error message.

        https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-an-error-message
        """
        stream = stream or sys.stderr
        loc = f'file={file},line={line},col={col}' if file else ''
        info = f' {loc}' if loc else ''
        print(f'::error{info}::{description}', file=stream)

    @staticmethod
    def warn(
        description: str,
        file: Optional[str] = None,
        line: Optional[str] = None,
        col: Optional[str] = None,
        stream: Optional[TextIO] = None,
    ) -> None:
        """Print a warning message.

        https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-a-warning-message
        """  # noqa
        stream = stream or sys.stderr
        loc = f'file={file},line={line},col={col}' if file else ''
        info = f' {loc}' if loc else ''
        print(f'::warning{info}::{description}', file=stream)


class Teamcity(CITool):
    """Collection of methods used to communicate with Teamcity."""

    @staticmethod
    def env_vars() -> OneOf[Issue, EnvVars]:
        """Read basic environment variables from Teamcity."""
        # WIP: Need to map the to the object
        return Good(EnvVars(ci_env=True))

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
        """Closes a previously defined block.

        See `open_block`.
        """
        print(f"##teamcity[blockClosed name='{name}']")

    @staticmethod
    def error(
        description: str,
        file: Optional[str] = None,
        line: Optional[str] = None,
        col: Optional[str] = None,
        stream: Optional[TextIO] = None,
    ) -> None:
        """Print a message to teamcity so that the build may abort."""
        stream = stream or sys.stderr
        parts = [x for x in [file, line, col] if x]
        loc = ':'.join(parts)
        info = f'[{loc}]: ' if loc else ''
        desc = Teamcity.escape_msg(f'{info}{description}' or '')
        print(
            f"##teamcity[buildProblem description='{desc}']",
            file=stream,
        )

    @staticmethod
    def warn(
        description: str,
        file: Optional[str] = None,
        line: Optional[str] = None,
        col: Optional[str] = None,
        stream: Optional[TextIO] = None,
    ) -> None:
        """Print a warning message to teamcity."""
        stream = stream or sys.stderr
        parts = [x for x in [file, line, col] if x]
        loc = ':'.join(parts)
        info = f'[{loc}]: ' if loc else ''
        desc = Teamcity.escape_msg(f'{info}{description}' or '')
        print(
            f"##teamcity[message status='WARNING' text='{desc}']",
            file=stream,
        )


def get_ci_tool() -> Type[CITool]:
    """Return the current CI Tool based on the environment variables."""
    if env('GITHUB_ACTIONS'):
        return GithubActions
    if env('TC') or env('TEAMCITY'):
        return Teamcity
    return CITool


CiTool = get_ci_tool()


def error_block(issue_: str, stream: TextIO = sys.stderr) -> None:
    """Print an issue within an error block."""
    CiTool.open_block('error', '')
    print(issue_, file=stream)
    CiTool.close_block('error')


def warn_block(issue_: str, stream: TextIO = sys.stderr) -> None:
    """Print an issue within a warning block."""
    CiTool.open_block('warning', '')
    print(issue_, file=stream)
    CiTool.close_block('warning')
