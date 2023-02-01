from functools import partial

import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase, assert_streams, run_cli
from tests.util import file_exists_mock, read_fixture_mock

FIXTURE_PATH = 'cli/commands/fixtures'


def _file_exists(name: str):
    """Having issues using partial with file_exists_mock."""
    return file_exists_mock(name, FIXTURE_PATH)


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m json oops',
        errors=[
            'failed to parse the json data',
            'json.decoder.JSONDecodeError:',
        ],
        exit_code=2,
    ),
    TCase(
        cmd='m json []',
        expected='[]'
    ),
    TCase(
        cmd=[
            'm',
            'json',
            '--sort-keys',
            '{"c": 3, "z": 99, "a": 1}',
        ],
        expected="""
          {
            "a": 1,
            "c": 3,
            "z": 99
          }
        """,
    ),
    TCase(
        cmd='m json',
        std_in='["a", "b"]',
        expected="""
          [
            "a",
            "b"
          ]
        """,
    ),
    TCase(
        cmd='m json',
        std_in='oops',
        errors=[
            '"message": "failed to read json file"',
            '"filename": "SYS.STDIN"',
            'json.decoder.JSONDecodeError',
        ],
        exit_code=2,
    ),
    TCase(
        cmd='m json @simple.json',
        expected="""
          [
            "a",
            0
          ]
        """,
    ),
    TCase(
        cmd='m json @invalid-file.json',
        errors=[
            'argument payload: file "invalid-file.json" does not exist',
        ],
        exit_code=2
    ),
    TCase(
        cmd='m json @bad_json.json',
        errors=[
            'argument payload: invalid json payload in bad_json.json',
        ],
        exit_code=2
    )
])
def test_m_json(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch('pathlib.Path.exists', _file_exists)
    mocker.patch(
        'pathlib.Path.open',
        partial(
            read_fixture_mock,
            mocker=mocker,
            path=FIXTURE_PATH,
        ),
    )

    if tcase.std_in:
        stdin_read = mocker.patch('sys.stdin.read')
        stdin_read.return_value = tcase.std_in

    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
