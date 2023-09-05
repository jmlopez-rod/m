import os
from textwrap import dedent

import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli

env_mock = {'NO_COLOR': 'true', 'HOME': '/home/user', 'DEBUG_M_LOGS': 'true'}


class TCase(CliTestCase):
    """Test case for `m devcontainer require_env_vars`."""

    work_dir: str = '/workspaces/repo_test'
    pnpm_dir: str = '/opt/pnpm/repo_test'
    cmd: str = 'm devcontainer pnpm_setup'
    exit_code: int = 0
    files_exists: list[str] = []
    symlinks_exists: list[str] = []
    dirs_created: list[str] = []
    total_symlinks: int = 0
    total_unlinks: int = 0


def _file_exists(name: str, tcase: TCase):
    return str(name) in tcase.files_exists


def _symlink_exists(name: str, tcase: TCase):
    return str(name) in tcase.symlinks_exists


@pytest.mark.parametrize('tcase', [
    pytest.param(
        TCase(
            exit_code=1,
            errors=[
                'missing_package_json',
                '/workspaces/repo_test',
                'directory does not have package.json',
                'you may create one with pnpm init',
            ],
            dirs_created=[],
        ),
        id='no_package',
    ),
    pytest.param(
        TCase(
            exit_code=1,
            errors=[
                'missing_npmrc',
                '"npmrc_work": "MISSING /workspaces/repo_test/.npmrc"',
                '"npmrc_home": "MISSING /home/user/.npmrc"',
            ],
            dirs_created=[
                '/opt/pnpm/repo_test',
                '/opt/pnpm/repo_test/node_modules',
            ],
            files_exists=['/workspaces/repo_test/package.json'],
            total_unlinks=0,
            total_symlinks=2,
        ),
        id='no_npmrc',
    ),
    pytest.param(
        TCase(
            exit_code=1,
            files_exists=[
                '/workspaces/repo_test/.npmrc',
                '/workspaces/repo_test/node_modules',
                '/workspaces/repo_test/package.json',
            ],
            errors=[
                'non_devcontainer_setup',
                '"work_node_modules": "/workspaces/repo_test/node_modules"',
                '"pnpm_node_modules": "/opt/pnpm/repo_test/node_modules"',
                '"remove all node_modules found in the project directory"',
            ],
            dirs_created=[
                '/opt/pnpm/repo_test',
            ],
            total_unlinks=0,
            total_symlinks=1,
        ),
        id='existing_node_modules_on_workspace',
    ),
    pytest.param(
        TCase(
            exit_code=0,
            files_exists=[
                '/workspaces/repo_test/.npmrc',
                '/workspaces/repo_test/package.json',
            ],
            errors=[
                '"work_lock": "MISSING /workspaces/repo_test/pnpm-lock.yaml"',
                '"suggestion": "run `pnpm install` to generate the lock file"',
            ],
            dirs_created=[
                '/opt/pnpm/repo_test',
                '/opt/pnpm/repo_test/node_module',
            ],
            total_unlinks=0,
            total_symlinks=3,
        ),
        id='no_lock_file',
    ),
    pytest.param(
        TCase(
            exit_code=0,
            files_exists=[
                '/workspaces/repo_test/.npmrc',
                '/workspaces/repo_test/package.json',
            ],
            symlinks_exists=[
                '/workspaces/repo_test/pnpm-lock.yaml',
            ],
            errors=[
                '"work_lock": "MISSING /workspaces/repo_test/pnpm-lock.yaml"',
                '"suggestion": "run `pnpm install` to generate the lock file"',
            ],
            dirs_created=[
                '/opt/pnpm/repo_test',
                '/opt/pnpm/repo_test/node_module',
            ],
            expected=dedent("""
                [DEBUG] [09:33:09 PM - Nov 29, 1973]: pnpm_setup_summary
                        {
                          "node_modules": "/workspaces/repo_test/node_modules -> /opt/pnpm/repo_test/node_modules",
                          "package": "/opt/pnpm/repo_test/package.json -> /workspaces/repo_test/package.json",
                          "npmrc": "/opt/pnpm/repo_test/.npmrc -> /workspaces/repo_test/.npmrc",
                          "pnpm_lock": "unlinked symlink /workspaces/repo_test/pnpm-lock.yaml"
                        }
                """),
            total_unlinks=1,
            total_symlinks=3,
        ),
        id='workdir_no_lock_symlink_please',
    ),
    pytest.param(
        TCase(
            exit_code=0,
            files_exists=[
                '/workspaces/repo_test/.npmrc',
                '/workspaces/repo_test/package.json',
                '/workspaces/repo_test/pnpm-lock.yaml',
            ],
            symlinks_exists=[
                '/workspaces/repo_test/node_modules',
                '/opt/pnpm/repo_test/package.json',
                '/opt/pnpm/repo_test/.npmrc',
                '/opt/pnpm/repo_test/pnpm-lock.yaml',
            ],
            errors=[],
            dirs_created=[
                '/opt/pnpm/repo_test',
                '/opt/pnpm/repo_test/node_module',
            ],
            expected=dedent("""
                [DEBUG] [09:33:09 PM - Nov 29, 1973]: pnpm_setup_summary
                        {
                          "node_modules": "/workspaces/repo_test/node_modules -> /opt/pnpm/repo_test/node_modules",
                          "package": "/opt/pnpm/repo_test/package.json -> /workspaces/repo_test/package.json",
                          "npmrc": "/opt/pnpm/repo_test/.npmrc -> /workspaces/repo_test/.npmrc",
                          "pnpm_lock": null
                        }
                """),
            total_unlinks=3,
            total_symlinks=3,
        ),
        id='right_setup',
    ),
])
def test_pnpm_setup(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, env_mock, clear=True)
    mocker.patch('time.time').return_value = 123456789
    mocker.patch(
        'pathlib.Path.exists',
        lambda name: _file_exists(name, tcase),
    )
    mocker.patch(
        'pathlib.Path.is_symlink',
        lambda name: _symlink_exists(name, tcase),
    )
    mkdir_mock = mocker.patch('pathlib.Path.mkdir')
    unlink_mock = mocker.patch('pathlib.Path.unlink')
    symlink_mock = mocker.patch('pathlib.Path.symlink_to')
    cmd = f'{tcase.cmd} {tcase.work_dir} {tcase.pnpm_dir}'
    std_out, std_err = run_cli(cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
    # Not sure how to get the caller of the method. The path that it was
    # used to call mkdir is the Path instance (the caller).
    assert mkdir_mock.call_count == len(tcase.dirs_created)
    assert (unlink_mock.call_count, symlink_mock.call_count) == (
        tcase.total_unlinks,
        tcase.total_symlinks,
    )
