import sys
from typing import TextIO

from m.core.io import env

from .providers.github import tool as gh_tool
from .providers.local import tool as local_tool
from .providers.teamcity import tool as tc_tool
from .types import ProviderModule

# Do not use outside of module. This is done here to avoid
# disabling a flake8 for every ci tool method.
_print = print


def get_ci_tool() -> ProviderModule:
    """Return the current CI Tool based on the environment variables.

    Returns:
        A `ProviderModule` instance with methods to provide messages in
        a CI environment.
    """
    if env('GITHUB_ACTIONS'):
        return gh_tool
    if env('TC') or env('TEAMCITY'):
        return tc_tool
    return local_tool


def error_block(msg: str, stream: TextIO | None = None) -> None:
    """Print an issue within an error block.

    Args:
        msg: The error message to display.
        stream: The file stream to print (defaults to sys.stderr)
    """
    tool = get_ci_tool()
    tool.open_block('error', '', stream or sys.stderr)
    _print(msg, file=stream or sys.stderr)
    tool.close_block('error', stream or sys.stderr)


def warn_block(msg: str, stream: TextIO | None = None) -> None:
    """Print an issue within a warning block.

    Args:
        msg: The warning message to display.
        stream: The file stream to print (defaults to sys.stderr)
    """
    tool = get_ci_tool()
    tool.open_block('warning', '', stream or sys.stderr)
    _print(msg, file=stream or sys.stderr)
    tool.close_block('warning', stream or sys.stderr)
