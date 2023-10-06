import os
import socket
from functools import partial
from typing import Any

from pydantic import BaseModel


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

    the `Path.mkdir` function should only be blocked while developing tests.
    It is a reminder that we haven't mocked the function yet. If we want to
    get this reminder then add `touch m/.m/pytest-ran` after the tests run
    locally.

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
        # To do so we will mock the Path.mkdir function. There is a problem:
        # pytest needs this function to create directories for its own purposes.
        # For this reason we will only mock the function after we create the
        # m/.m/pytest-ran file.
        if Path('m/.m/pytest-ran').exists():
            Path.mkdir = mock('pathlib.Path.mkdir')  # type: ignore

    return originals
