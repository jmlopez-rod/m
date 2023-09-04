import os
import shutil
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
from m.core import Good, issue
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli

env_mock = {'NO_COLOR': 'true', 'HOME': '/home/user', 'DEBUG_M_LOGS': 'true'}
m_env = {
    'MDC_WORKSPACE': '/workspaces/repo_name',
    'MDC_PNPM_WORKSPACE': '/opt/pnpm/repo_name',
}


class TCase(CliTestCase):
    """Test case for `m devcontainer require_env_vars`."""

    pnpm_args: str
    cmd: str = 'm devcontainer pnpm'
    exit_code: int = 0
    cwd: str = '/workspaces/repo_name'
    files_exists: list[str] = []
    symlinks_exists: list[str] = []
    environ: dict[str, str] = {}
    exec_pnpm: Any = Good(None)
    pnpm_exec_dir: str | None = None
    move_args: tuple[str, str] | None = None
    store_path_res: bool = True


def _file_exists(name: str, tcase: TCase):
    return str(name) in tcase.files_exists


def _symlink_exists(name: str, tcase: TCase):
    return str(name) in tcase.symlinks_exists


@pytest.mark.parametrize('tcase', [
    pytest.param(
        TCase(
            exit_code=1,
            pnpm_args='',
            errors=[
                'missing_env_var',
                '"MDC_WORKSPACE": null',
                '"MDC_PNPM_WORKSPACE": null',
                '"suggestion": "are you running this command from a devcontainer?"',
            ],
        ),
        id='missing_env_vars',
    ),
    pytest.param(
        TCase(
            exit_code=1,
            environ=m_env,
            cwd='/opt/checking/things/out',
            pnpm_args='',
            errors=[
                'invalid_devcontainer_pnpm_use',
                '"workdir": "/opt/checking/things/out"',
                'pnpm alias should only be run in the `workspace',
                'the original `pnpm` may be used by running `command pnpm`',
            ],
        ),
        id='pnpm_outside_workspace',
    ),
    pytest.param(
        TCase(
            exit_code=0,
            environ=m_env,
            pnpm_args='',
        ),
        id='pnpm_no_args',
    ),
    pytest.param(
        TCase(
            exit_code=1,
            environ=m_env,
            pnpm_args='install',
            errors=[
                'missing_package_json',
                '"warning": "run pnpm commands in directories with package.json"',
            ],
        ),
        id='missing_package_json',
    ),
    pytest.param(
        TCase(
            exit_code=1,
            environ=m_env,
            pnpm_args='install',
            errors=[
                'invalid_pnpm_setup',
                '"error": "/workspaces/repo_name/node_modules is not a symlink"',
            ],
            files_exists=[
                '/workspaces/repo_name/package.json',
            ],
        ),
        id='bad_setup_node_modules_not_symlink',
    ),
    pytest.param(
        TCase(
            exit_code=1,
            environ=m_env,
            pnpm_args='install',
            errors=[
                'invalid_pnpm_setup',
                '"error": "/opt/pnpm/repo_name/.npmrc is not a symlink"',
            ],
            files_exists=[
                '/workspaces/repo_name/package.json',
            ],
            symlinks_exists=[
                '/workspaces/repo_name/node_modules',
            ],
        ),
        id='bad_setup_no_npmrc_symlink',
    ),
    pytest.param(
        TCase(
            exit_code=0,
            environ=m_env,
            pnpm_args='install',
            files_exists=[
                '/workspaces/repo_name/package.json',
            ],
            symlinks_exists=[
                '/workspaces/repo_name/node_modules',
                '/opt/pnpm/repo_name/.npmrc',
            ],
            pnpm_exec_dir='/opt/pnpm/repo_name',
            expected=dedent("""
                [INFO] [09:33:09 PM - Nov 29, 1973]: executing_pnpm_in_mounted_volume
                       {
                         "store_path": "/opt/pnpm/made/up/store",
                         "pnpm_dir": "/opt/pnpm/repo_name"
                       }
                """),
            move_args=(
                '/opt/pnpm/repo_name/pnpm-lock.yaml',
                '/workspaces/repo_name/pnpm-lock.yaml',
            ),
        ),
        id='pnpm_install_first_time',
    ),
    pytest.param(
        TCase(
            exit_code=0,
            environ=m_env,
            pnpm_args='install',
            files_exists=[
                '/workspaces/repo_name/package.json',
            ],
            symlinks_exists=[
                '/workspaces/repo_name/node_modules',
                '/opt/pnpm/repo_name/.npmrc',
                '/opt/pnpm/repo_name/pnpm-lock.yaml',
            ],
            pnpm_exec_dir='/opt/pnpm/repo_name',
            expected=dedent("""
                [INFO] [09:33:09 PM - Nov 29, 1973]: executing_pnpm_in_mounted_volume
                       {
                         "store_path": "/opt/pnpm/made/up/store",
                         "pnpm_dir": "/opt/pnpm/repo_name"
                       }
                """),
            move_args=(
                '/opt/pnpm/repo_name/pnpm-lock.yaml',
                '/workspaces/repo_name/pnpm-lock.yaml',
            ),
        ),
        id='pnpm_install_established',
    ),
    pytest.param(
        TCase(
            exit_code=1,
            environ=m_env,
            pnpm_args='install',
            files_exists=[
                '/workspaces/repo_name/package.json',
            ],
            symlinks_exists=[
                '/workspaces/repo_name/node_modules',
                '/opt/pnpm/repo_name/.npmrc',
                '/opt/pnpm/repo_name/pnpm-lock.yaml',
            ],
            pnpm_exec_dir='/opt/pnpm/repo_name',
            expected=dedent("""
                [INFO] [09:33:09 PM - Nov 29, 1973]: executing_pnpm_in_mounted_volume
                       {
                         "store_path": "/opt/pnpm/made/up/store",
                         "pnpm_dir": "/opt/pnpm/repo_name"
                       }
                """),
            exec_pnpm=issue('oh no... something wrong'),
        ),
        id='pnpm_error',
    ),
    pytest.param(
        TCase(
            exit_code=1,
            environ=m_env,
            pnpm_args='hotdog',
            files_exists=[
                '/workspaces/repo_name/package.json',
            ],
            symlinks_exists=[
                '/workspaces/repo_name/node_modules',
                '/opt/pnpm/repo_name/.npmrc',
                '/opt/pnpm/repo_name/pnpm-lock.yaml',
            ],
            exec_pnpm=issue('yeah..., this command does not exist'),
        ),
        id='pnpm_error_hotdog',
    ),
    pytest.param(
        TCase(
            exit_code=1,
            environ=m_env,
            pnpm_args='install',
            files_exists=[
                '/workspaces/repo_name/package.json',
            ],
            symlinks_exists=[
                '/workspaces/repo_name/node_modules',
                '/opt/pnpm/repo_name/.npmrc',
                '/opt/pnpm/repo_name/pnpm-lock.yaml',
            ],
            errors=['oops... undefined store'],
            store_path_res=False,
        ),
        id='pnpm_error_bad_store',
    ),
])
def test_pnpm_cli(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {**env_mock, **tcase.environ}, clear=True)
    mocker.patch('time.time').return_value = 123456789
    chdir_mock = mocker.patch.object(os, 'chdir')
    move_mock = mocker.patch.object(shutil, 'move')
    mocker.patch.object(Path, 'cwd').return_value = Path(tcase.cwd)
    mocker.patch(
        'pathlib.Path.exists',
        lambda name: _file_exists(name, tcase),
    )
    mocker.patch(
        'pathlib.Path.is_symlink',
        lambda name: _symlink_exists(name, tcase),
    )
    mocker.patch('pathlib.Path.unlink')
    mocker.patch('pathlib.Path.symlink_to')
    mocker.patch('m.core.subprocess.exec_pnpm').return_value = tcase.exec_pnpm
    store_path = '/opt/pnpm/made/up/store'
    store_path_mock = mocker.patch('m.core.subprocess.eval_cmd')
    if tcase.store_path_res:
        store_path_mock.return_value = Good(store_path)
    else:
        store_path_mock.return_value = issue('oops... undefined store')
    cmd = f'{tcase.cmd} {tcase.pnpm_args}'
    std_out, std_err = run_cli(cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
    if tcase.pnpm_exec_dir:
        chdir_mock.assert_called_once_with(tcase.pnpm_exec_dir)
    if tcase.move_args:
        move_mock.assert_called_once_with(*tcase.move_args)
    else:
        move_mock.assert_not_called()
