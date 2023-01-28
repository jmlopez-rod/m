import math
import os
import sys
from typing import TypeVar

from m.core import Good, Issue, OneOf, issue
from pydantic import BaseModel

BaseModelT = TypeVar('BaseModelT', bound=BaseModel)


def format_seconds(number_of_seconds: int | float) -> str:
    """Return a string representing the number of seconds in a friendly
    format: Xd:Xh:Xm:Xs:Xms. """
    milliseconds = int(math.floor(number_of_seconds * 1000))
    _ms = milliseconds % 1000
    seconds = int(math.floor(milliseconds / 1000))
    sec = seconds % 60
    minutes = int(math.floor(seconds / 60))
    mins = minutes % 60
    hours = int(math.floor(minutes / 60))
    hrs = hours % 24
    days = int(math.floor(hours / 24))

    entries = [
        f'{days}d' if days else '',
        f'{hrs}h' if hours else '',
        f'{mins}m' if mins else '',
        f'{sec}s' if sec else '',
        f'{_ms}ms' if _ms else '',
    ]
    return ':'.join([x for x in entries if x]) or '0s'


def env(name: str, def_val: str = '') -> str:
    """Access an environment variable.

    Args:
        name: The name of the environment variable.
        def_val: The default value to return if not set. Defaults to empty.

    Returns:
        The value of the environment variable if set otherwise the `def_val`.
    """
    return os.environ.get(name, def_val)


def renv(key: str) -> OneOf[Issue, str]:
    """Require an environment variable to be defined.

    Args:
        key: The environment variable required to be defined.

    Returns:
        A `OneOf` with the value of the environment variable or an issue.
    """
    value = os.environ.get(key)
    # Value may still be an empty string, checking against None
    if value is not None:
        return Good(value)
    return issue(f'missing {key} in env')


def env_model(model: type[BaseModelT]) -> OneOf[Issue, BaseModelT]:
    """Require multiple env vars to be defined.

    This can be done by defining a model::

        class GithubEnvVars(BaseModel):
            repo: str = Field('GITHUB_REPOSITORY')
            run_id: str = Field('GITHUB_RUN_ID')

    Then we use it::

        print(env.repo for env in env_model(GithubEnvVars)])

    Args:
        model: A pydantic model specifying the environment variables to fetch.

    Returns:
        A `OneOf` with the values of the environment variables or an issue.
    """
    schema = model.schema()
    missing: list[str] = []
    env_values: dict[str, str] = {}
    for name, field in schema['properties'].items():
        env_name = field.get('default')
        env_value = os.environ.get(env_name)
        if env_value is None:
            missing.append(env_name)
        else:
            env_values[name] = env_value
    if missing:
        missing_str = ', '.join(missing)
        return issue(f'missing [{missing_str}] in env')
    return Good(model(**env_values))


def _ver_str(major: int, minor: int, patch: int) -> str:
    return f'{major}.{minor}.{patch}'


def prompt_next_version(version: str, release_type: str) -> str:
    """Display the possible major, minor and patch versions and prompt the user
    to enter one of them. Return one of the versions.

    https://semver.org/
    """
    ver = version.split('-')[0]
    parts = [int(x) for x in ver.split('.')]
    patch = _ver_str(parts[0], parts[1], parts[2] + 1)
    if release_type == 'hotfix':
        return patch

    minor = _ver_str(parts[0], parts[1] + 1, 0)
    major = _ver_str(parts[0] + 1, 0, 0)
    valid = False
    options = [minor, major]
    msg = f'Current version is {version}. Enter one of the following:\n  '
    msg += '\n  '.join(options)
    result = ''
    while not valid:
        print(msg, file=sys.stderr)
        result = input('')
        if result in options:
            valid = True
    return result
