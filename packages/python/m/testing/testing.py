import os
import socket
from functools import partial
from typing import Any

from pydantic import BaseModel, Field


class BlockNetwork(socket.socket):
    """Implements a socket that blocks all network calls."""

    # pylint: disable-next=super-init-not-called
    def __init__(self, *args: Any, **kwargs: Any):
        """Raise an error if called.

        Args:
            args: ...
            kwargs: ...

        Raises:
            RuntimeError: Always.
        """
        raise RuntimeError('Network call blocked')


class ActionStepTestCase(BaseModel):
    """Defines a test case for an action.

    Useful in the parametrization of several use cases for an action.
    """

    name: str = Field(description="""
        Unique name for the test case. This is used as the identifier
        for a test case so that test failures may be easier to spot.
    """)

    py_file: str = Field(description='Path to the python file to run.')

    inputs: dict[str, str] = Field(description="""
        Inputs to the script. Should be of the form

        ```py
        {'INPUT_[SOME_NAME]': 'value'}
        ```
    """)

    exit_code: int = Field(
        default=0,
        description='The expected exit code (default: 0).',
    )

    expected_stdout: str = Field(
        default='',
        description='The expected stdout (default: empty).',
    )

    # Errors may be noisy, specify strings that are expected to be in stderr
    errors: list[str] = Field(
        default=[],
        description="""
            Errors may be noisy, specify strings that are expected to be in stderr
            in an array of strings.
        """,
    )

    # list of outputs: `output-name=output-value`
    outputs: list[str] = Field(
        default=[],
        description="""
            list of Github outputs. Each entry in the array should be of the form

            ```
            output-name=output-value
            ```
        """,
    )

    file_write_side_effect: Any | None = Field(
        default=None,
        description="""
            Defaults to [`Good(0)`][m.core.fp.Good]. This can be provided if we
            need to modify the behavior of [m.core.rw.write_file][]. This is
            useful if we want to test cases in which a file failed to write.
        """,
    )


def needs_mocking(func_name: str, *args: Any, **kwargs: Any):
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

    This function overrides the definition of [`socket`][socket.socket] so that
    we do not accidentally try to run tests that make network calls. If our tests
    do not depend on other local services it is a good idea to call this before
    any of our tests runs.

    Otherwise we may want to modify this function to allow certain hosts to be
    called. (PRs welcomed).
    """
    # making sure that no calls to the internet are done
    socket.socket = BlockNetwork  # type: ignore


def block_m_side_effects() -> dict[str, Any]:
    """Blocks functions that have side effects.

    This function overrides the definition of `m` so that we do not accidentally
    try write a lot of files or create/move directories.

    The [pathlib.Path.mkdir][] function should only be blocked while developing
    tests. It is a reminder that we haven't mocked the function yet. If we want
    to get this reminder then add `touch m/.m/pytest-ran` after the tests run
    locally.

    Returns:
        A dictionary with references to the original functions that were
            overridden in case these are needed.
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
