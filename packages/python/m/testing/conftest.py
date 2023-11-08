"""
This module is provided to help with testing.

The following external modules are expected to be available:

- [pytest][]
- [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/)
"""
import os
import runpy
import sys
from io import StringIO
from typing import Any

import pytest
from m.core import Good
from pytest_mock import MockerFixture

from .testing import ActionStepTestCase


def run_action_step(
    mocker: MockerFixture,
    *,
    py_file: str,
    exit_code: int,
    env_vars: dict[str, str],
    file_write_side_effect: Any | None = None,
) -> tuple[str, str, dict[str, str]]:
    """Execute an action step in a test.

    This function expects the inputs to the script to be provided via environment
    variables of the form `INPUT_[SOME_NAME]`. The script will write the outputs
    to the file `FAKE_GITHUB_OUTPUT.txt`. We can verify the contents of the file
    by looking at the 3rd output from the function. This is a dictionary mapping
    file names to contents. Please note that this testing function mocks
    [m.core.rw.write_file][] to obtain the file contents.

    Args:
        mocker: A reference to the pytest `MockerFixture`.
        py_file: The full path to the file that Github Actions will run.
        exit_code: The expected exit code of the action. `0` means all is good.
        env_vars: A dictionary of the environment variables that the action will
            receive.
        file_write_side_effect: This can be provided if we need to modify the
            behavior of [m.core.rw.write_file][]. This is useful if we want to
            test cases in which a file failed to write.

    Returns:
        The standard out, standard error, and files written by [m.core.rw.write_file][].
    """
    mocker.patch.dict(
        os.environ,
        {
            'NO_COLOR': 'true',
            **env_vars,
            'GITHUB_OUTPUT': 'FAKE_GITHUB_OUTPUT.txt',
        },
        clear=True,
    )

    std_out = StringIO()
    std_err = StringIO()
    mocker.patch.object(sys, 'stdout', std_out)
    mocker.patch.object(sys, 'stderr', std_err)
    file_write_mock = mocker.patch('m.core.rw.write_file')
    file_write_mock.side_effect = file_write_side_effect or [Good(0)]

    prog = None
    with pytest.raises(SystemExit) as prog_block:
        prog = prog_block
        runpy.run_path(py_file, {}, '__main__')

    # Would be nice to be able to reset via a the mocker
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    assert prog is not None  # noqa: S101 - to be used in testing
    file_writes = {
        call.args[0]: call.args[1]
        for call in file_write_mock.call_args_list
    }

    # next block should not be covered by coverage, we have this as a utility
    # to help us write tests.
    prog_code = prog.value.code
    if prog_code != exit_code:  # pragma: no cover
        print(std_out.getvalue(), file=sys.stdout)  # noqa: WPS421
        print(std_err.getvalue(), file=sys.stderr)  # noqa: WPS421
    assert prog_code == exit_code   # noqa: S101 - to be used in testing
    return std_out.getvalue(), std_err.getvalue(), file_writes


def run_action_test_case(
    mocker: MockerFixture,
    tcase: ActionStepTestCase,
) -> None:
    """Execute an action step test case.

    This is a commodity wrapper to help us run the action tests case. If we need
    more control over the assertions we can then copy and modify the implementation.

    Args:
        mocker: A reference to the pytest `MockerFixture`.
        tcase: The test case.
    """
    stdout, stderr, file_writes = run_action_step(
        mocker,
        py_file=tcase.py_file,
        exit_code=tcase.exit_code,
        env_vars=tcase.inputs,
        file_write_side_effect=tcase.file_write_side_effect,
    )
    assert stdout == tcase.expected_stdout  # noqa: S101
    if tcase.errors:
        for error in tcase.errors:
            assert error in stderr  # noqa: S101

    if tcase.exit_code == 0:
        assert 'FAKE_GITHUB_OUTPUT.txt' in file_writes  # noqa: S101
        gh_output = file_writes['FAKE_GITHUB_OUTPUT.txt']
        assert gh_output == '\n'.join(tcase.outputs)  # noqa: S101
