"""
This module is provided to help with testing.

The following external modules are expected to be available:

- pytest
- pytest_mock
"""
import os
import runpy
import socket
import sys
from functools import partial
from io import StringIO
from typing import Any

import pytest
from m.core import Good
from pydantic import BaseModel
from pytest_mock import MockerFixture


class BlockNetwork(socket.socket):
    """Implements a socket that blocks all network calls."""

    # pylint: disable-next=super-init-not-called
    def __init__(self, *args, **kwargs):
        """Raise an error if called.

        Args:
            args: ...
            kwargs: ...

        Raises:
            RuntimeError: Always.
        """
        raise RuntimeError('Network call blocked')


class ActionStepTestCase(BaseModel):
    """A test case for an action step."""

    # id of the test
    name: str

    # path to the python file to run
    py_file: str

    # the inputs to the script {'INPUT_[SOME_NAME]': 'value'}
    inputs: dict[str, str]

    # The expected exit code
    exit_code: int = 0

    # The expected stdout
    expected_stdout: str = ''

    # Errors may be noisy, specify strings that are expected to be in stderr
    errors: list[str] = []

    # list of outputs: `output-name=output-value`
    outputs: list[str] = []

    # By default we make it return `Good(0)`. But may be modified to return
    # something else.
    file_write_side_effect: Any | None = None


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
    `m.core.rw.write_file` to obtain the file contents.

    Args:
        mocker: The mocker fixture.
        py_file: The path to the python file to run.
        exit_code: The expected exit code.
        env_vars: The environment variables to set.
        file_write_side_effect: Optional side effect to return from file_write.

    Returns:
        The standard out, standard error, and file writes.
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
        # display the captured stderr to debug
        print(  # noqa: WPS421
            f'EXIT CODE MISMATCH: expected {exit_code}, got {prog_code}',
            file=sys.stderr,
        )
        print(std_out.getvalue(), file=sys.stdout)  # noqa: WPS421
        print(std_err.getvalue(), file=sys.stderr)  # noqa: WPS421
    assert prog_code == exit_code   # noqa: S101 - to be used in testing
    return std_out.getvalue(), std_err.getvalue(), file_writes


def needs_mocking(func_name: str, *args, **kwargs):
    """Raise an exception asking developer to mock a function.

    Args:
        func_name: name of the function
        args: ...
        kwargs: ...

    Raises:
        RuntimeError: Always.
    """
    raise RuntimeError(f'DEV ERROR: Need to mock {func_name}({args},{kwargs})')


def mock(func_name: str) -> Any:
    """Create a function that raises an error if its not mocked.

    Args:
        func_name: full module path to the function to mock.

    Returns:
        A function that raises an error if its not mocked.
    """
    return partial(needs_mocking, func_name)


def block_network_access() -> None:
    """Blocks network access for all tests.

    This is useful to ensure that tests do not make any network calls.
    """
    # making sure that no calls to the internet are done
    socket.socket = BlockNetwork  # type: ignore


def block_m_side_effects() -> dict[str, Any]:
    """Blocks functions that have side effects.

    Returns:
        A dictionary with the original functions.
    """
    import shutil
    import subprocess  # noqa: S404 - importing to disable it during testing
    from pathlib import Path

    from m.core import rw as mio

    originals = {
        'write_file': mio.write_file,
        'Path_mkdir': Path.mkdir,
        'shutil_move': shutil.move,
    }

    mio.write_file = mock('m.core.rw.write_file')
    subprocess.check_output = mock('m.core.subprocess.eval_cmd')
    subprocess.call = mock('m.core.subprocess.exec_pnpm')
    shutil.move = mock('shutil.move')

    if not os.environ.get('CI'):
        # We want to make sure that we do not create directories during tests.
        # To do we we will mock the Path.mkdir function. There is a problem:
        # pytest needs this function to create directories for its own purposes.
        # For this reason we will only mock the function after we create the
        # m/.m/pytest-ran file.
        if Path('m/.m/pytest-ran').exists():
            Path.mkdir = mock('pathlib.Path.mkdir')  # type: ignore

    return originals
