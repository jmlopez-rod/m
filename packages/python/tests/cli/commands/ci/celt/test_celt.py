import os
from functools import partial

import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import run_cli
from tests.util import file_exists_mock, read_fixture, read_fixture_mock

FIXTURE_PATH = 'cli/commands/ci/celt/fixtures'


def _file_exists(name: str):
    """Having issues using partial with file_exists_mock."""
    return file_exists_mock(name, FIXTURE_PATH)


def _get_fixture(name: str):
    return read_fixture(name, FIXTURE_PATH)


class TCase(CliTestCase):
    expected_file: str


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m ci celt -c @cfg_01.json -t pycodestyle @pycodestyle.txt',
        expected_file='cfg_01_expected.txt',
        exit_code=1,
    ),
    TCase(
        cmd='m ci celt -c @cfg_01.json -t invalid_tool @pycodestyle.txt',
        expected_file='cfg_01_invalid_tool.txt',
        exit_code=1,
    ),
])
def test_m_ci_celt(tcase: TCase, mocker: MockerFixture) -> None:
    # clear env vars to avoid ci tool specific messages
    mocker.patch.dict(os.environ, {}, clear=True)
    mocker.patch('pathlib.Path.exists', _file_exists)
    mocker.patch(
        'pathlib.Path.open',
        partial(
            read_fixture_mock,
            mocker=mocker,
            path=FIXTURE_PATH,
        ),
    )

    _, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert std_err == _get_fixture(tcase.expected_file)
