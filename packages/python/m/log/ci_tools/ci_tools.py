from m.core import io as mio

from .providers.github import tool as gh_tool
from .providers.local import tool as local_tool
from .providers.teamcity import tool as tc_tool
from .types import ProviderModule


def get_ci_tool() -> ProviderModule:
    """Return the current CI Tool based on the environment variables.

    Returns:
        A `ProviderModule` instance with methods to provide messages in
        a CI environment.
    """
    env = mio.env
    if env('GITHUB_ACTIONS'):
        return gh_tool
    if env('TC') or env('TEAMCITY'):
        return tc_tool
    return local_tool
