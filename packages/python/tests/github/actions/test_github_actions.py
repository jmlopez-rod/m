import os
from pathlib import Path

import pytest
from m.core import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import assert_streams, run_cli
from tests.util import read_fixture

from .conftest import TCase, WriteArgs

BASE_DIR = 'packages/python/tests/github/actions'

FILE_ISSUES = [
    TCase(
        name='bad_file',
        py_file='not_here.py',
        errors=[
            '"message": "file does not exist"',
            '"path": "not_here.py"',
        ],
        exit_code=1,
    ),
    TCase(
        name='not_a_module',
        py_file='README.md',
        errors=[
            '"message": "import_module_failure"',
            '"message": "No module named \'README\'"',
        ],
        exit_code=1,
    ),
    TCase(
        name='actions_not_found',
        py_file='packages/python/m/git.py',
        errors=[
            '"message": "missing_attribute"',
            '"missing_attribute": "actions"',
        ],
        exit_code=1,
    ),
    TCase(
        name='wrong_single_action',
        py_file=f'{BASE_DIR}/wrong_actions/single.py',
        errors=[
            '"message": "invalid_actions"',
            '"ensure all actions are of type \\"m.github.actions.Action\\""',
        ],
        exit_code=1,
    ),
    TCase(
        name='wrong_multiple_actions',
        py_file=f'{BASE_DIR}/wrong_actions/multiple.py',
        errors=[
            '"message": "invalid_actions"',
            '"ensure all actions are of type \\"m.github.actions.Action\\""',
        ],
        exit_code=1,
    ),
]

WRITING_FILES = [
    TCase(
        name='square_num',
        py_file=f'{BASE_DIR}/square_number/actions.py',
        write_calls=[
            WriteArgs(
                path='actions.yaml',
                fname='square_number.yaml',
            ),
        ],
    ),
    TCase(
        name='multiple',
        py_file=f'{BASE_DIR}/multiple/actions.py',
        write_calls=[
            WriteArgs(
                path='multiple/action.yaml',
                fname='multiple-action.yaml',
            ),
            WriteArgs(
                path='multiple/action-empty.yaml',
                fname='multiple-action-empty.yaml',
            ),
        ],
    ),
]

@pytest.mark.parametrize(
    'tcase',
    [
        *FILE_ISSUES,
        *WRITING_FILES,
    ],
    ids=lambda tcase: tcase.name,
)
def test_m_gh_actions(tcase: TCase, mocker: MockerFixture) -> None:
    """Test `m github actions` errors.

    Args:
        tcase: The test case.
        mocker: The pytest mocker.
    """
    mocker.patch.dict(
        os.environ,
        {
            'GITHUB_TOKEN': '***',
            'NO_COLOR': 'true',
        },
        clear=True,
    )
    mocker.patch('time.time').return_value = 123456789
    file_write_mock = mocker.patch('m.core.rw.write_file')
    file_write_mock.return_value = Good(0)

    cmd = f'{tcase.cmd} {tcase.py_file}'
    if tcase.checks:
        cmd += ' --check'
    std_out, std_err = run_cli(cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)

    calls = file_write_mock.call_args_list
    assert len(calls) == len(tcase.write_calls)
    fixture_path = 'github/actions/_fixtures'
    for index, ex_call in enumerate(tcase.write_calls):
        call = calls[index]
        assert Path(call.args[0]).resolve() == Path(ex_call.path).resolve()
        assert call.args[1] == read_fixture(ex_call.fname, fixture_path)
