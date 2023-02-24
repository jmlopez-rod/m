import math
import os
import sys
from typing import Sequence, TypeVar

from m.color import color
from m.core import Good, OneOf
from m.core.issue import Issue
from m.core.one_of import issue
from m.log.logger import Logger
from pydantic import BaseModel

BaseModelT = TypeVar('BaseModelT', bound=BaseModel)
logger = Logger('m.core.io')


def _is_true(name: str) -> bool:
    return env(name, 'false') == 'true'


def is_traceback_enabled() -> bool:
    """Return True if the stacktrace should be displayed.

    This is true by default on a CI environment where the env var CI is set
    to `true`.

    We can enable this locally by settings the env vars

    - DEBUG_M_STACKTRACE
    - DEBUG

    The `DEBUG_M_STACKTRACE` is provided so to only target this particular
    piece of info and avoid other pieces of code that may be looking at
    the `DEBUG` env var from activating.

    Returns:
        True if the stacktrace should be displayed.
    """
    debug_stacktrace = _is_true('DEBUG_M_STACKTRACE')
    debug_mode = _is_true('DEBUG')
    ci_env = _is_true('CI')
    return debug_stacktrace or debug_mode or ci_env


def is_python_info_enabled():
    """Return True if the python file location should be displayed.

    By default this information is not displayed since the stacktrace already
    provides most of the info. If we need it we can set one of the env var

    - DEBUG_M_PYTHON
    - DEBUG

    `DEBUG_M_PYTHON` is accepted in case we do not want to enable the
    traceback.

    Returns:
        True if the python file location should be displayed.
    """
    debug_python = _is_true('DEBUG_M_PYTHON')
    debug_mode = _is_true('DEBUG')
    return debug_python or debug_mode


def format_seconds(number_of_seconds: int | float) -> str:
    """Return a string representing the number of seconds.

    The format is Xd:Xh:Xm:Xs:Xms.

    Args:
        number_of_seconds: The number of seconds to format.

    Returns:
        A friendly representation of the number of seconds.
    """
    milliseconds = int(math.floor(number_of_seconds * 1000))
    milli_sec = milliseconds % 1000
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
        f'{milli_sec}ms' if milli_sec else '',
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
    env_value = os.environ.get(key)
    # Value may still be an empty string, checking against None
    if env_value is not None:
        return Good(env_value)
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


def prompt_next_version(version: str, release_type: str) -> OneOf[Issue, str]:
    """Prompt the developer to select the next version.

    It displays the possible major, minor and patch versions and prompts the
    developer to enter one of them. See https://semver.org/.

    Args:
        version: The current version.
        release_type: If `hotfix` then it bumps the patch value.

    Returns:
        One of the versions wrapped in a OneOf.
    """
    ver = version.split('-')[0]
    parts = [int(x) for x in ver.split('.')]
    patch = _ver_str(parts[0], parts[1], parts[2] + 1)
    if release_type == 'hotfix':
        return Good(patch)

    minor = _ver_str(parts[0], parts[1] + 1, 0)
    major = _ver_str(parts[0] + 1, 0, 0)
    ver = f'{{bold_green}}{version}{{end}}'
    msg = color(f'Current version is {ver}. Enter one of the following:')
    return Good(prompt_choices(msg, [minor, major]))


def prompt_choices(
    description: str,
    choices: Sequence[str],
    as_list=True,
) -> str:
    """Prompt the user with a description until we get one of the choices.

    Args:
        description: The prompt to display.
        choices: List of accepted choices.
        as_list: If false, it will concat the choices with `/`.

    Returns:
        The string chosen by the user.
    """
    valid = False
    dev_input = ''
    choices_display = choices if as_list else '/'.join(choices)
    while not valid:
        logger.prompt(description, {'choices': choices_display})
        sys.stderr.write('>>>>>>>> ')
        dev_input = input()
        if dev_input in choices:
            valid = True
    return dev_input
