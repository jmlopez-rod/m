import os
import socket
import subprocess
from functools import partial
from pathlib import Path

from m.core import Issue
from m.core import rw as mio

original_write_file = mio.write_file
original_mkdir = Path.mkdir


# Disabling yaml output - during tests we want to focus on json data
Issue.yaml_traceback = False


def needs_mocking(func_name: str, *args, **kwargs):
    """"Raise an exception asking developer to mock a function.

    Args:
        func_name: name of the function
        args: ...
        kwargs: ...
    """
    raise Exception(f'DEV ERROR: Need to mock {func_name}({args},{kwargs})')


def mock(func_name: str):
    """Assign a function that raises an error if its not mocked."""
    return partial(needs_mocking, func_name)


mio.write_file = mock('m.core.rw.write_file')
subprocess.check_output = mock('m.core.subprocess.eval_cmd')
subprocess.call = mock('m.core.subprocess.exec_pnpm')

if not os.environ.get('CI'):
    # We want to make sure that we do not create directories during tests.
    # To do we we will mock the Path.mkdir function. There is a problem though:
    # pytest needs this function to create directories for its own purposes.
    # For this reason we will only mock the function after we create the
    # m/.m/pytest-ran file.
    if Path('m/.m/pytest-ran').exists():
        Path.mkdir = mock('pathlib.Path.mkdir')  # type: ignore


class BlockNetwork(socket.socket):
    def __init__(self, *args, **kwargs):
        raise Exception('Network call blocked')


# making sure that no calls to the internet are done
socket.socket = BlockNetwork  # type: ignore
