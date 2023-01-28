import os
import sys
from io import StringIO
from typing import cast

from m.cli.utils import error
from m.core import Issue
from m.core.ci_tools import EnvVars, get_ci_tool, warn_block
from pytest_mock import MockerFixture


def mock_streams(mocker: MockerFixture):
    std_out = StringIO()
    std_err = StringIO()
    mocker.patch.object(sys, 'stdout', std_out)
    mocker.patch.object(sys, 'stderr', std_err)
    return std_out, std_err


def test_ci_tool_warn_block(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {}, clear=True)
    std_out, std_err = mock_streams(mocker)
    warn_block('message to stdout', sys.stdout)
    assert std_out.getvalue() == 'warning:\nmessage to stdout\n\n'
    assert std_err.getvalue() == ''


def test_ci_tool_warn_block_err(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {}, clear=True)
    std_out, std_err = mock_streams(mocker)
    warn_block('message to stderr', sys.stderr)
    assert std_out.getvalue() == ''
    assert std_err.getvalue() == 'warning:\nmessage to stderr\n\n'


def test_ci_tool_github_plain_str(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {'GITHUB_ACTIONS': 'true'}, clear=True)
    std_out, std_err = mock_streams(mocker)
    tool = get_ci_tool()
    tool.error('some error')
    tool.warn('some warning')
    assert std_out.getvalue() == ''

    err = std_err.getvalue()
    assert err == '::error::some error\n::warning::some warning\n'


def test_ci_tool_tc_plain_str(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {'TC': 'true'}, clear=True)
    std_out, std_err = mock_streams(mocker)
    tool = get_ci_tool()
    tool.error('some error')
    tool.warn('some warning')
    assert std_out.getvalue() == ''

    err = std_err.getvalue()
    assert err == '\n'.join([
        "##teamcity[buildProblem description='some error']",
        "##teamcity[message status='WARNING' text='some warning']",
        '',
    ])

    # Only verifying that there we are in a ci environment to get
    # full coverage for tc.
    either = tool.env_vars()
    assert not either.is_bad
    assert cast(EnvVars, either.value).ci_env is True


def test_cli_util_error_no_block(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {'GITHUB_ACTIONS': 'true'}, clear=True)
    std_out, std_err = mock_streams(mocker)
    error('some error')
    assert std_out.getvalue() == ''
    err = std_err.getvalue()
    assert err == '::error::some error\n'


def test_cli_util_error_block(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {'GITHUB_ACTIONS': 'true'}, clear=True)
    std_out, std_err = mock_streams(mocker)
    error('some error', issue=Issue('oops'))
    assert std_out.getvalue() == ''
    err = std_err.getvalue()
    assert err.startswith('::error::some error\n')
    assert '"message": "oops"' in err
