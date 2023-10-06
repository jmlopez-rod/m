import pytest
from m.core import issue
from m.testing import ActionStepTestCase as TCase
from m.testing import run_action_test_case
from pytest_mock import MockerFixture

BASE_DIR = 'packages/python/tests/github/actions'


def mock_file_write(*args, **kwargs):
    raise Exception('unknown exception')


@pytest.mark.parametrize(
    'tcase',
    [
        TCase(
            name='square_number',
            py_file=f'{BASE_DIR}/square_number/main.py',
            inputs={'INPUT_NUM': '4'},
            expected_stdout='square-number action running\n',
            outputs=['num-squared=16'],
        ),
        TCase(
            name='square_number_yaml_error',
            py_file=f'{BASE_DIR}/square_number/main.py',
            inputs={'NUM': '4'},  # missing the correct input
            exit_code=4,
            errors=[
                '"message": "load_step_inputs_failure"',
                '"message": "1 validation error for GithubInputs',
            ],
        ),
        TCase(
            name='square_number_bad_write',
            py_file=f'{BASE_DIR}/square_number/main.py',
            inputs={'INPUT_NUM': '4'},
            exit_code=6,
            errors=[
                '"message": "bad write"',
            ],
            expected_stdout='square-number action running\n',
            file_write_side_effect=[issue('bad write')],
        ),
        TCase(
            name='square_number_write_exception',
            py_file=f'{BASE_DIR}/square_number/main.py',
            inputs={'INPUT_NUM': '4'},
            exit_code=5,
            errors=[
                '"message": "dump_step_outputs"',
                '"message": "unknown exception"',
            ],
            expected_stdout='square-number action running\n',
            file_write_side_effect=mock_file_write,
        ),
    ],
    ids=lambda tcase: tcase.name,
)
def test_m_gh_actions_api(tcase: TCase, mocker: MockerFixture) -> None:
    run_action_test_case(mocker, tcase)
