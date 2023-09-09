import os

import pytest
from m.devcontainer.bashrc import bashrc_snippet, devex_snippet
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli


class TCase(CliTestCase):
    """Test case for `m devcontainer require_env_vars`."""

    environ: dict[str, str]
    cmd: str = 'm devcontainer bashrc'
    exit_code: int = 0
    section: str | None = None
    cleandoc: bool = False


@pytest.mark.parametrize('tcase', [
    TCase(
        environ={'VAR1': 'one', 'VAR2': 'two'},
        expected='\n'.join([
            "export MDC_REPO='ERROR_UNKNOWN_WORKSPACE'",
            "export MDC_WORKSPACE='ERROR_UNKNOWN_WORKSPACE'",
            "export MDC_PNPM_WORKSPACE='/opt/pnpm/ERROR_UNKNOWN_WORKSPACE'",
            "export MDC_VENV_WORKSPACE='/opt/venv/ERROR_UNKNOWN_WORKSPACE'",
            bashrc_snippet,
        ]),
    ),
    TCase(
        environ={'GITHUB_WORKSPACE': '/__w/sub_folder/repo_name'},
        expected='\n'.join([
            "export MDC_REPO='repo_name'",
            "export MDC_WORKSPACE='/__w/sub_folder/repo_name'",
            "export MDC_PNPM_WORKSPACE='/opt/pnpm/repo_name'",
            "export MDC_VENV_WORKSPACE='/opt/venv/repo_name'",
            bashrc_snippet,
        ]),
    ),
    TCase(
        environ={'CONTAINER_WORKSPACE': '/workspace/repo_name'},
        expected='\n'.join([
            "export MDC_REPO='repo_name'",
            "export MDC_WORKSPACE='/workspace/repo_name'",
            "export MDC_PNPM_WORKSPACE='/opt/pnpm/repo_name'",
            "export MDC_VENV_WORKSPACE='/opt/venv/repo_name'",
            bashrc_snippet,
        ]),
    ),
    TCase(
        section='devex',
        environ={'CONTAINER_WORKSPACE': '/workspace/repo_name'},
        expected=devex_snippet,
    ),
])
def test_bashrc(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(
        os.environ,
        {'NO_COLOR': 'true', **tcase.environ},
        clear=True,
    )
    cmd = tcase.cmd
    if tcase.section:
        cmd = f'{cmd} --section {tcase.section}'
    std_out, std_err = run_cli(cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
