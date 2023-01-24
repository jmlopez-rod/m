import sys
from typing import TextIO

from m.core.io import env

from .providers.github import tool as gh_tool
from .providers.local import tool as local_tool
from .providers.teamcity import tool as tc_tool
from .types import ProviderModule


def get_ci_tool() -> ProviderModule:
    """Return the current CI Tool based on the environment variables."""
    if env('GITHUB_ACTIONS'):
        return gh_tool
    if env('TC') or env('TEAMCITY'):
        return tc_tool
    return local_tool


def error_block(issue_: str, stream: TextIO | None = None) -> None:
    """Print an issue within an error block."""
    tool = get_ci_tool()
    tool.open_block('error', '')
    print(issue_, file=stream or sys.stderr)
    tool.close_block('error')


def warn_block(issue_: str, stream: TextIO | None = None) -> None:
    """Print an issue within a warning block."""
    tool = get_ci_tool()
    tool.open_block('warning', '')
    print(issue_, file=stream or sys.stderr)
    tool.close_block('warning')
