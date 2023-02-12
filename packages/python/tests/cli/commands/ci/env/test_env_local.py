import os
from functools import partial

import pytest
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import run_cli
from tests.util import read_fixture, read_fixture_mock

FIXTURE_PATH = 'cli/commands/ci/env/fixtures'


def _get_fixture(name: str):
    return read_fixture(name, FIXTURE_PATH)


class TCase(CliTestCase):
    git_branch: str
    current_commit_sha: str
    m_list_file: str
    m_list_contents: str


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m ci env m_dir_local',
        git_branch='master',
        current_commit_sha='abc123',
        m_list_file='m_dir_local/.m/env.list',
        m_list_contents='m_dir_local/m_expected.list',
    ),
])
def test_m_ci_env_local(tcase: TCase, mocker: MockerFixture) -> None:
    # clear env vars to avoid ci tool specific messages
    mocker.patch.dict(os.environ, {}, clear=True)
    mocker.patch('pathlib.Path.exists').return_value = False
    mocker.patch('pathlib.Path.mkdir')
    mocker.patch(
        'pathlib.Path.open',
        partial(
            read_fixture_mock,
            mocker=mocker,
            path=FIXTURE_PATH,
        ),
    )
    mocker.patch('m.git.get_branch').return_value = Good(tcase.git_branch)
    mocker.patch('m.git.get_current_commit_sha').return_value = Good(
        tcase.current_commit_sha,
    )
    mocker.patch('time').return_value = 123456789
    write_file_mock = mocker.patch('m.core.rw.write_file')
    write_file_mock.return_value = Good(None)

    run_cli(tcase.cmd, tcase.exit_code, mocker)
    write_file_mock.assert_called_once()
    file_name, file_contents = write_file_mock.call_args[0]
    assert file_name == tcase.m_list_file
    assert file_contents == _get_fixture(tcase.m_list_contents).strip()
