import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase, assert_streams, run_cli


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m --version',
        expected='0.0.0-PLACEHOLDER',
    ),
    TCase(
        cmd='m',
        errors=[
            'the following arguments are required: <command>',
        ],
        exit_code=2,
    ),
])
def test_m_npm_clean_tags(tcase: TCase, mocker: MockerFixture) -> None:
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
