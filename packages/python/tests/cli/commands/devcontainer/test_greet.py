import os
from textwrap import dedent

import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli

env_mock = {'NO_COLOR': 'true'}


class TCase(CliTestCase):
    """Test case for `m devcontainer require_env_vars`."""

    cmd_args: list[str]
    cmd: str = 'm devcontainer greet'
    exit_code: int = 0


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd_args=[
            '--img-name my-devcontainer',
            '--img-version 1.0.0',
        ],
        expected=dedent("""
            [INFO] [09:33:09 PM - Nov 29, 1973]: container_ready
                   {
                     "name": "my-devcontainer",
                     "version": "1.0.0",
                     "TIP": "set `DEBUG`/`DEBUG_M_LOGS` to true to display debugging info"
                   }
            """),
    ),
    TCase(
        cmd_args=[
            '--img-name my-devcontainer',
            '--img-version 1.0.0',
            '--changelog-url https://changelog_url.com',
        ],
        expected=dedent("""
            [INFO] [09:33:09 PM - Nov 29, 1973]: container_ready
                   {
                     "name": "my-devcontainer",
                     "version": "1.0.0",
                     "TIP": "set `DEBUG`/`DEBUG_M_LOGS` to true to display debugging info",
                     "changelog": "https://changelog_url.com#1.0.0"
                   }
            """),
    ),
])
def test_greet(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, env_mock, clear=True)
    mocker.patch('time.time').return_value = 123456789
    cmd_args = ' '.join(tcase.cmd_args)
    cmd = f'{tcase.cmd} {cmd_args}'
    std_out, std_err = run_cli(cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
