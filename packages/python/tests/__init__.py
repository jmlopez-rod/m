import subprocess
from m.core import rw as mio
from functools import partial


def needs_mocking(func_name: str, *args, **kwargs):
    """"Raise an exception asking developer to mock a function.

    Args:
        func_name: name of the function
        args: ...
        kwargs: ...
    """
    raise RuntimeError(f'DEV ERROR: Need to mock {func_name}!!!')


def mock(func_name: str):
    """Assign a function that raises an error if its not mocked."""
    return partial(needs_mocking, func_name)


mio.write_file = mock('mock m.core.rw.write_file')
subprocess.check_output = mock('m.core.subprocess.eval_cmd')
