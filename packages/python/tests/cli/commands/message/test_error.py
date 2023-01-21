import os

import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli


class TCase(CliTestCase):
    """Test case for `m message`."""

    environ: dict[str, str] = {}
    exit_code: int = 1


LH: dict = {}  # Localhost
GH = {'GITHUB_ACTIONS': 'true'}  # Github
TC = {'TEAMCITY': 'true'}  # Teamcity
MSG = 'hot dog, hot dog, hot diggity dog'
FN = 'pkg/file.py'

SIMPLE = [
    TCase(
        cmd=['m', 'message', 'error', MSG],
        errors=[err_msg],
        environ=env_vars,
    )
    for err_msg, env_vars in (
        (f'error: {MSG}\n', LH),
        (f'::error::{MSG}\n', GH),
        (f"##teamcity[buildProblem description='{MSG}']\n", TC),
    )
]
WITH_FILE = [
    TCase(
        cmd=['m', 'message', 'error', '-f', FN, MSG],
        errors=[err_msg],
        environ=env_vars,
    )
    for err_msg, env_vars in (
        (f'error[{FN}]: {MSG}\n', LH),
        (f'::error file={FN}::{MSG}\n', GH),
        (f"##teamcity[buildProblem description='|[{FN}|]: {MSG}']\n", TC),
    )
]
WITH_LINE = [
    TCase(
        cmd=['m', 'message', 'error', '-f', FN, '-l', '99', MSG],
        errors=[err_msg],
        environ=env_vars,
    )
    for err_msg, env_vars in [
        (f'error[{FN}:99]: {MSG}\n', LH),
        (f'::error file={FN},line=99::{MSG}\n', GH),
        (f"##teamcity[buildProblem description='|[{FN}:99|]: {MSG}']\n", TC),
    ]
]
WITH_COL = [
    TCase(
        cmd=['m', 'message', 'error', '-f', FN, '-l', '1', '-c', '2', MSG],
        errors=[err_msg],
        environ=env_vars,
    )
    for err_msg, env_vars in [
        (f'error[{FN}:1:2]: {MSG}\n', LH),
        (f'::error file={FN},line=1,col=2::{MSG}\n', GH),
        (f"##teamcity[buildProblem description='|[{FN}:1:2|]: {MSG}']\n", TC),
    ]
]


@pytest.mark.parametrize('tcase', [
    *SIMPLE,
    *WITH_FILE,
    *WITH_LINE,
    *WITH_COL,
    TCase(
        cmd='m message error',
        errors=[
            'the following arguments are required: message',
        ],
        exit_code=2,
    ),
])
def test_m_message_error(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, tcase.environ, clear=True)
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
