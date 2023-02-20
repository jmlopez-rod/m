import os
from functools import partial

import pytest
from m.core import Bad, Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli
from tests.util import file_exists_mock, read_fixture, read_fixture_mock

FIXTURE_PATH = 'cli/commands/fixtures'


class TCase(CliTestCase):

    cmd: str = 'm init'
    repo_url: str
    m_file_exists: bool = False
    changelog_exists: bool = False
    gitignore_contents: str = '.vscode\nm/.m\n'
    new_gitignore_contents: str = '.vscode\nm/.m\n'
    changelog: str | None = None
    m_file: str | None = None


def _file_exists(name: str, tcase: TCase):
    """Having issues using partial with file_exists_mock."""
    if str(name) == 'm/m.json':
        return tcase.m_file_exists
    if str(name) == 'CHANGELOG.md':
        return tcase.changelog_exists
    return file_exists_mock(name, FIXTURE_PATH)


def _eval_cmd(cmd: str, tcase: TCase):
    if cmd == 'git config --get remote.origin.url':
        return Good(tcase.repo_url)
    if cmd == 'touch .gitignore':
        return Good(0)
    return Bad(f'need to mock: {cmd}')


@pytest.mark.parametrize('tcase', [
    TCase(
        repo_url='git@github.com:jmlopez-rod/m.git',
        expected=read_fixture('m_init_blank.log', FIXTURE_PATH),
        errors=[
            '[WARNING]',
            '.gitignore already ignores m/.m',
        ],
    ),
    TCase(
        repo_url='git@github.com:jmlopez-rod/m.git',
        changelog_exists=True,
        errors=[
            '[WARNING]',
            'CHANGELOG.md already exists',
        ],
        expected=read_fixture('m_init_blank_clog.log', FIXTURE_PATH),
    ),
    TCase(
        repo_url='https://github.com/jmlopez-rod/m',
        errors=['unable to obtain owner and repo'],
        new_line=False,
        exit_code=1,
    ),
    TCase(
        repo_url='git@github.com:fizzy/hotdog.git',
        expected=read_fixture('m_init_repeat.log', FIXTURE_PATH),
        errors=[
            '[WARNING]',
            'm/m.json already exists',
        ],
        cleandoc=False,
        new_line=False,
        changelog_exists=True,
        m_file_exists=True,
    ),
    TCase(
        repo_url='git@github.com:fizzy/hotdog.git',
        expected=read_fixture('m_init_blank_hotdog.log', FIXTURE_PATH),
        gitignore_contents='npm_modules\nhotdog',
        new_gitignore_contents='npm_modules\nhotdog\nm/.m\n',
        changelog='CHANGELOG.md',
        m_file='m_fake.json',
    ),
])
def test_m_init(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {'NO_COLOR': 'true'}, clear=True)
    mocker.patch('time.time').return_value = 123456789
    mocker.patch(
        'pathlib.Path.exists',
        lambda name: _file_exists(name, tcase),
    )
    mocker.patch('pathlib.Path.mkdir')
    mocker.patch(
        'pathlib.Path.open',
        partial(
            read_fixture_mock,
            mocker=mocker,
            path=FIXTURE_PATH,
        ),
    )
    mocker.patch(
        'm.core.subprocess.eval_cmd',
        lambda cmd: _eval_cmd(cmd, tcase),
    )
    # Only testing the case in which it writes
    file_write_mock = mocker.patch('m.core.rw.write_file')
    file_write_mock.return_value = Good(0)

    # There is only one file we are expecting to read
    file_read_mock = mocker.patch('m.core.rw.read_file')
    file_read_mock.return_value = Good(tcase.gitignore_contents)

    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)

    if std_err:
        return

    # Check file contents only if there are no errors
    all_calls = file_write_mock.call_args_list
    m_call = all_calls[0]
    if tcase.m_file:
        assert m_call.args == (
            'm/m.json',
            read_fixture(tcase.m_file, FIXTURE_PATH),
        )

    gitignore_call = all_calls[1]
    if tcase.gitignore_contents:
        assert gitignore_call.args == (
            '.gitignore',
            tcase.new_gitignore_contents,
        )

    changelog_call = all_calls[2]
    if tcase.changelog:
        assert changelog_call.args == (
            'CHANGELOG.md',
            read_fixture('CHANGELOG.md', FIXTURE_PATH),
        )
