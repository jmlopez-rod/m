import os
from inspect import cleandoc

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
TC_RES = """
    ##teamcity[blockClosed name='old']
    ##teamcity[blockOpened name='new' description='a desc']
"""

TESTS = [
    TCase(
        cmd=['m', 'message', 'sibling_block', 'old', 'new', 'a desc'],
        expected=msg,
        environ=env_vars,
        cleandoc=False,
    )
    for msg, env_vars in (
        ('\n  >>> [new]: a desc', LH),
        ('::endgroup::\n::group::new - a desc', GH),
        (cleandoc(TC_RES), TC),
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
def test_m_message_sibling(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, tcase.environ, clear=True)
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
