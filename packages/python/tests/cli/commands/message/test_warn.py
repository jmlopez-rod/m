import os

import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli


class TCase(CliTestCase):
    """Test case for `m message`."""

    environ: dict[str, str] = {}
    exit_code: int = 0


LH: dict = {}  # Localhost
GH = {'GITHUB_ACTIONS': 'true'}  # Github
TC = {'TEAMCITY': 'true'}  # Teamcity
MSG = 'hot dog, hot dog, hot diggity dog'
FN = 'pkg/file.py'
LP = '[WARNING] [09:33:09 PM - Nov 29, 1973]'

WARN = "message status='WARNING'"
SIMPLE = [
    TCase(
        cmd=['m', 'message', 'warn', MSG],
        errors=[err_msg],
        environ=env_vars,
    )
    for err_msg, env_vars in (
        (f'{LP}: {MSG}\n', LH),
        (f'::warning::{MSG}\n', GH),
        (f"##teamcity[{WARN} text='{MSG}']\n", TC),
    )
]
WITH_FILE = [
    TCase(
        cmd=['m', 'message', 'warn', '-f', FN, MSG],
        errors=[err_msg],
        environ=env_vars,
    )
    for err_msg, env_vars in [
        (f'{LP}[{FN}]: {MSG}\n', LH),
        (f'::warning file={FN}::{MSG}\n', GH),
        (f"##teamcity[{WARN} text='|[{FN}|]: {MSG}']\n", TC),
    ]
]
WITH_LINE = [
    TCase(
        cmd=['m', 'message', 'warn', '-f', FN, '-l', '99', MSG],
        errors=[err_msg],
        environ=env_vars,
    )
    for err_msg, env_vars in [
        (f'{LP}[{FN}:99]: {MSG}\n', LH),
        (f'::warning file={FN},line=99::{MSG}\n', GH),
        (f"##teamcity[{WARN} text='|[{FN}:99|]: {MSG}']\n", TC),
    ]
]
WITH_COL = [
    TCase(
        cmd=['m', 'message', 'warn', '-f', FN, '-l', '1', '-c', '2', MSG],
        errors=[err_msg],
        environ=env_vars,
    )
    for err_msg, env_vars in [
        (f'{LP}[{FN}:1:2]: {MSG}\n', LH),
        (f'::warning file={FN},line=1,col=2::{MSG}\n', GH),
        (f"##teamcity[{WARN} text='|[{FN}:1:2|]: {MSG}']\n", TC),
    ]
]


@pytest.mark.parametrize('tcase', [
    *SIMPLE,
    *WITH_FILE,
    *WITH_LINE,
    *WITH_COL,
    TCase(
        cmd='m message warn',
        errors=[
            'the following arguments are required: message',
        ],
        exit_code=2,
    ),
])
def test_m_message_warn(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, tcase.environ, clear=True)
    mocker.patch('time.time').return_value = 123456789
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
