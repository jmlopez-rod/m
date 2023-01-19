import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase, assert_streams, run_cli


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
    )
])
def test_m_json(tcase: TCase, mocker: MockerFixture) -> None:
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
