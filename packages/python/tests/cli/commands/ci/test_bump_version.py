import pytest
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli


class TCase(CliTestCase):
    """Test case for `m ci bump_version`."""

    input_side_effects: list[str]


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m ci bump_version --type release 0.0.1',
        input_side_effects=['wrong', '0.2.0', '1.0.0'],
        expected='1.0.0',
    ),
    TCase(
        cmd='m ci bump_version --type release 0.0.1',
        input_side_effects=['wrong', 'oops', '0.1.0'],
        expected='0.1.0',
    ),
    TCase(
        cmd='m ci bump_version --type hotfix 0.0.1',
        input_side_effects=['0.0.2'],
        expected='0.0.2',
    ),
    TCase(
        cmd='m ci bump_version',
        input_side_effects=[],
        errors=['the following arguments are required: --type, version'],
        exit_code=2,
    ),
])
def test_m_ci_bump_version(tcase: TCase, mocker: MockerFixture) -> None:
    eval_cmd = mocker.patch('builtins.input')
    eval_cmd.side_effect = tcase.input_side_effects
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
