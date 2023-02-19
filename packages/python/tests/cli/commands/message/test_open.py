import os

import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli


class TCase(CliTestCase):
    """Test case for `m message`."""

    environ: dict[str, str] = {}
    exit_code: int = 0


LH: dict = {'NO_COLOR': 'true'}  # Localhost
GH = {'GITHUB_ACTIONS': 'true', 'NO_COLOR': 'true'}  # Github
TC = {'TEAMCITY': 'true', 'NO_COLOR': 'true'}  # Teamcity

TESTS = [
    TCase(
        cmd=['m', 'message', 'open', 'title', 'a desc'],
        expected=msg,
        environ=env_vars,
        cleandoc=False,
    )
    for msg, env_vars in (
        ('  >>> [title]: a desc', LH),
        ('::group::title - a desc', GH),
        ("##teamcity[blockOpened name='title' description='a desc']", TC),
    )
]


@pytest.mark.parametrize('tcase', [
    *TESTS,
    TCase(
        cmd='m message open',
        errors=[
            'the following arguments are required: name, description',
        ],
        exit_code=2,
    ),
])
def test_m_message_open(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, tcase.environ, clear=True)
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
