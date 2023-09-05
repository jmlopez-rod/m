import os
from pathlib import Path
from typing import Any

import pytest
from m.core import Good, issue, subprocess
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli


class TCase(CliTestCase):
    """Test case for `m devcontainer require_env_vars`."""

    environ: dict[str, str] = {}
    cmd: str = 'm devcontainer prompter'
    exit_code: int = 0
    branch: Any
    status: Any | None = None
    repo_path: Any | None = None
    cwd: str | None = None
    rev_parse_side_effect: Any | None = None
    no_color: str = 'true'
    new_line: bool = False


@pytest.mark.parametrize('tcase', [
    pytest.param(
        TCase(
            expected=r'\w$ ',
            branch=issue('not in a git repo'),
        ),
        id='no_git',
    ),
    pytest.param(
        TCase(
            # wants me to write `\w` but then what do I do with \x1b?
            expected='\x1b[38;5;172m\\w\x1b[0m$ \x1b[0m',  # noqa: WPS342
            branch=issue('not in a git repo'),
            no_color='false',
        ),
        id='no_git_with_color',
    ),
    pytest.param(
        TCase(
            expected=' '.join([
                '\x1b[38;5;82m➜ devcontainer:repo',
                '[\x1b[38;5;82m✔ master] ^$ ',
            ]),
            cwd='/home/user/repo',
            branch=Good('master'),
            status=Good(('clean', 'working tree clean')),
            repo_path=Good('/home/user/repo'),
        ),
        id='clean',
    ),
    pytest.param(
        TCase(
            expected=' '.join([
                '\x1b[38;5;142m➜ devcontainer:repo',
                '[\x1b[38;5;142m◀ topic/feature]',
                '^/some/dir/in/repo$ ',
            ]),
            cwd='/home/user/repo/some/dir/in/repo',
            branch=Good('topic/feature'),
            status=Good(('behind', 'Your branch is behind')),
            repo_path=Good('/home/user/repo'),
        ),
        id='relative_path',
    ),
    pytest.param(
        TCase(
            expected=' '.join([
                '\x1b[38;5;142m➜ my-container@1.2.3:repo',
                '[\x1b[38;5;142m◀ topic/feature]',
                '^/some/dir/in/repo$ ',
            ]),
            environ={
                'DK_CONTAINER_NAME': 'my-container',
                'DK_CONTAINER_VERSION': '1.2.3',
            },
            cwd='/home/user/repo/some/dir/in/repo',
            branch=Good('topic/feature'),
            status=Good(('behind', 'Your branch is behind')),
            repo_path=Good('/home/user/repo'),
        ),
        id='container_version',
    ),
    pytest.param(
        TCase(
            expected=' '.join([
                '\x1b[38;5;142m➜ my-container@rc123.abc:repo',
                '[\x1b[38;5;142m◀ topic/feature]',
                '^/some/dir/in/repo$ ',
            ]),
            environ={
                'DK_CONTAINER_NAME': 'my-container',
                'DK_CONTAINER_VERSION': '0.0.0-rc123.abc',
            },
            cwd='/home/user/repo/some/dir/in/repo',
            branch=Good('topic/feature'),
            status=Good(('behind', 'Your branch is behind')),
            repo_path=Good('/home/user/repo'),
        ),
        id='container_version_rc',
    ),
    pytest.param(
        TCase(
            expected=' '.join([
                '\x1b[38;5;142m➜ my-container@[DEV]:repo',
                '[\x1b[38;5;142m◀ topic/feature]',
                '^/some/dir/in/repo$ ',
            ]),
            environ={
                'DK_CONTAINER_NAME': 'my-container',
                'DK_CONTAINER_VERSION': '0.0.0-local.abc',
            },
            cwd='/home/user/repo/some/dir/in/repo',
            branch=Good('topic/feature'),
            status=Good(('behind', 'Your branch is behind')),
            repo_path=Good('/home/user/repo'),
        ),
        id='container_version_dev',
    ),
    pytest.param(
        TCase(
            expected=' '.join([
                '\x1b[38;5;82m➜ my-container@[DEV]:repo',
                '[\x1b[38;5;82m✔ abcdef]',
                '^/some/dir/in/repo$ ',
            ]),
            environ={
                'DK_CONTAINER_NAME': 'my-container',
                'DK_CONTAINER_VERSION': '0.0.0-local.abc',
            },
            cwd='/home/user/repo/some/dir/in/repo',
            branch=Good('HEAD'),
            status=Good(('clean', 'working tree clean')),
            repo_path=Good('/home/user/repo'),
            rev_parse_side_effect=Good('abcdef'),
        ),
        id='short_sha',
    ),
    pytest.param(
        TCase(
            expected=' '.join([
                '\x1b[38;5;82m➜ my-container@[DEV]:repo',
                '[\x1b[38;5;82m✔ HEAD]',
                '^/some/dir/in/repo$ ',
            ]),
            environ={
                'DK_CONTAINER_NAME': 'my-container',
                'DK_CONTAINER_VERSION': '0.0.0-local.abc',
            },
            cwd='/home/user/repo/some/dir/in/repo',
            branch=Good('HEAD'),
            status=Good(('clean', 'working tree clean')),
            repo_path=Good('/home/user/repo'),
            rev_parse_side_effect=issue('no short sha for you'),
        ),
        id='no_short_sha',
    ),
])
def test_prompter(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(
        os.environ,
        {'NO_COLOR': tcase.no_color, **tcase.environ},
        clear=True,
    )
    if tcase.cwd:
        mocker.patch.object(Path, 'cwd').return_value = Path(tcase.cwd)
    if tcase.rev_parse_side_effect:
        eval_mock = mocker.patch.object(subprocess, 'eval_cmd')
        eval_mock.return_value = tcase.rev_parse_side_effect
    mocker.patch('m.git.get_branch').return_value = tcase.branch
    mocker.patch('m.git.get_status').return_value = tcase.status
    mocker.patch('m.git.get_repo_path').return_value = tcase.repo_path
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
