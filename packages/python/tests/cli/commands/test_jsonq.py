import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase, assert_streams, run_cli


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m jsonq [1] 0',
        expected='1',
    ),
    TCase(
        cmd=[
            'm',
            'jsonq',
            '{"a":{"b":{"c":["hello"] } } }',
            'a.b.c.0',
        ],
        expected='hello'
    ),
    TCase(
        cmd=[
            'm',
            'jsonq',
            '{"a":{"b":{"c":["hello"] } } }',
            'a.b.d.0',
        ],
        errors=[
            'multi_get key retrieval failure',
            'key lookup failure: `a.b.d.0`',
        ],
        exit_code=1,
    )
])
def test_m_jsonq(tcase: TCase, mocker: MockerFixture) -> None:
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
