import os
import socket
import subprocess
from functools import partial
from pathlib import Path

from m.core import rw as mio

original_write_file = mio.write_file
original_mkdir = Path.mkdir


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

if not os.environ.get('CI'):
    # LOOK AT ME!!! If you are running this locally you'll have to
    # do a first run with this line disabled. Pytest uses mkdir to
    # create some directories and doing this messes it up. So if its
    # the first time, disable and then enable. Only doing this so that
    # we are reminded that during tests we should mock making directories.
    Path.mkdir = mock('pathlib.Path.mkdir')  # type: ignore


class BlockNetwork(socket.socket):
    def __init__(self, *args, **kwargs):
        raise Exception("Network call blocked")


# making sure that no calls to the internet are done
socket.socket = BlockNetwork  # type: ignore
