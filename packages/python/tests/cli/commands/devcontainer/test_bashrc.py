import os

import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli


class TCase(CliTestCase):
    """Test case for `m devcontainer require_env_vars`."""

    environ: dict[str, str]
    cmd: str = 'm devcontainer bashrc'
    exit_code: int = 0


# end of snippet - making sure we keep track of this changes in testing.
snippet_end = (
    'alias pnpm="m devcontainer pnpm"',
    'alias np="m devcontainer pnpm"',
    "alias cd='HOME=$MDC_WORKSPACE cd'",
    'function prompter() { export PS1="$(m devcontainer prompter)"; }',
    'export PROMPT_COMMAND=prompter',
    'export VIRTUAL_ENV="$MDC_VENV_WORKSPACE"',
    'export PATH="$VIRTUAL_ENV/bin:$PATH"',
    '. "$VIRTUAL_ENV/bin/activate"',
)


@pytest.mark.parametrize('tcase', [
    TCase(
        environ={'VAR1': 'one', 'VAR2': 'two'},
        expected='\n'.join([
            "export MDC_REPO='ERROR_UNKNOWN_WORKSPACE'",
            "export MDC_WORKSPACE='ERROR_UNKNOWN_WORKSPACE'",
            "export MDC_PNPM_WORKSPACE='/opt/pnpm/ERROR_UNKNOWN_WORKSPACE'",
            "export MDC_VENV_WORKSPACE='/opt/venv/ERROR_UNKNOWN_WORKSPACE'",
            *snippet_end,
        ]),
    ),
    TCase(
        environ={'GITHUB_WORKSPACE': '/__w/sub_folder/repo_name'},
        expected='\n'.join([
            "export MDC_REPO='repo_name'",
            "export MDC_WORKSPACE='/__w/sub_folder/repo_name'",
            "export MDC_PNPM_WORKSPACE='/opt/pnpm/repo_name'",
            "export MDC_VENV_WORKSPACE='/opt/venv/repo_name'",
            *snippet_end,
        ]),
    ),
    TCase(
        environ={'CONTAINER_WORKSPACE': '/workspace/repo_name'},
        expected='\n'.join([
            "export MDC_REPO='repo_name'",
            "export MDC_WORKSPACE='/workspace/repo_name'",
            "export MDC_PNPM_WORKSPACE='/opt/pnpm/repo_name'",
            "export MDC_VENV_WORKSPACE='/opt/venv/repo_name'",
            *snippet_end,
        ]),
    ),
])
def test_bashrc(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(
        os.environ,
        {'NO_COLOR': 'true', **tcase.environ},
        clear=True,
    )
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
