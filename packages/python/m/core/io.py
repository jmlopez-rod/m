import os
import sys
from dataclasses import dataclass
from abc import ABC
from typing import Optional, Type, List, cast
from .. import git
from .fp import OneOf, Good, one_of
from .issue import Issue, issue


def env(name: str, def_val='') -> str:
    """Access an environment variable. Return empty string if not defined."""
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
        return Good(open(filename).read())
    except Exception as ex:
        return issue(
            'failed to read file',
            data={'filename': filename},
            cause=ex)


def write_file(filename: str, contents: str) -> OneOf[Issue, int]:
    """Return a `Good` containing 0 if the file was written."""
    try:
        with open(filename, 'w') as fp:
            fp.write(contents)
        return Good(0)
    except Exception as ex:
        return issue(
            'failed to write file',
            data={'filename': filename},
            cause=ex)


def _ver_str(major: int, minor: int, patch: int) -> str:
    return f'{major}.{minor}.{patch}'


def prompt_next_version(version: str) -> str:
    """Display the possible major, minor and patch versions and prompt
    the user to enter one of them. Return one of the versions.

    https://semver.org/
    """
    ver = version.split('-')[0]
    parts = [int(x) for x in ver.split('.')]
    patch = _ver_str(parts[0], parts[1], parts[2] + 1)
    minor = _ver_str(parts[0], parts[1] + 1, 0)
    major = _ver_str(parts[0] + 1, 0, 0)
    valid = False
    options = [patch, minor, major]
    msg = f'Current version is {version}. Enter one of the following:\n  '
    msg += '\n  '.join(options)
    result = ''
    while not valid:
        print(msg, file=sys.stderr)
        result = input('')
        if result in options:
            valid = True
    return result


@dataclass
class EnvVars:
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
    """Class representing a continuous integration tool. We can use this
    class static methods to display local messages."""

    @staticmethod
    def env_vars() -> OneOf[Issue, EnvVars]:
        """Obtain basic environment variables. """
        res = EnvVars()
        return one_of(lambda: [
            res
            for res.git_branch in git.get_branch()
            for res.git_sha in git.get_current_commit_sha()
        ])

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
    def env_vars() -> OneOf[Issue, EnvVars]:
        """Read the environment variables from Github Actions."""
        res = EnvVars(
            ci_env=True,
            server_url='https://github.com',
        )
        return one_of(lambda: [
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
                f'{res.server_url}/{repo}/actions/runs/{res.run_id}'
            ]
        ]).map_bad(lambda x: issue(
            'GH Actions env_vars failure', cause=cast(Issue, x)))

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


def error_block(issue_: str) -> None:
    """Print an issue within an error block"""
    CiTool.open_block('error', '')
    print(issue_, file=sys.stderr)
    CiTool.close_block('error')


def warn_block(issue_: str) -> None:
    """Print an issue within a warning block"""
    CiTool.open_block('warning', '')
    print(issue_, file=sys.stderr)
    CiTool.close_block('warning')
