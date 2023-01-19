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

TESTS = [
    TCase(
        cmd=['m', 'message', 'close', 'title'],
        expected=msg,
        environ=env_vars,
    )
    for msg, env_vars in (
        ('\n', LH),
        ('::endgroup::\n', GH),
        ("##teamcity[blockClosed name='title']\n", TC),
    )
]


@pytest.mark.parametrize('tcase', [
    *TESTS,
    TCase(
        cmd='m message close',
        errors=[
            'the following arguments are required: name',
        ],
        exit_code=2,
    ),
])
def test_m_message_close(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, tcase.environ)
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
