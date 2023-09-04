import os

import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli


class TCase(CliTestCase):
    """Test case for `m devcontainer require_env_vars`."""

    cmd_args: str
    environ: dict[str, str]
    cmd: str  = 'm devcontainer require_env_vars'
    exit_code: int = 2


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd_args='VAR1 VAR2',
        exit_code=0,
        environ={'VAR1': 'one', 'VAR2': 'two'},
    ),
    TCase(
        cmd_args='VAR1 VAR2 VAR3',
        environ={'VAR1': 'one', 'VAR2': 'two'},
        errors=[
            'missing_env_vars',
            '"VAR1": "one"',
            '"VAR2": "two"',
        ]
    ),
])
def test_require_env_vars(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(
        os.environ,
        {'NO_COLOR': 'true', **tcase.environ},
        clear=True,
    )
    cmd = f'{tcase.cmd} {tcase.cmd_args}'
    std_out, std_err = run_cli(cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
