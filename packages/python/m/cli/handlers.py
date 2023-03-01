
import json
from contextlib import suppress
from functools import partial
from typing import Any, Callable

from m.color import highlight_json, highlight_yaml
from m.core import Issue, yaml
from m.log import Logger

logger = Logger('m.cli.cli_helpers')


def _issue_handler(use_warning: bool, iss: Issue):
    """Log an Issue instance.

    Provides the user_warning argument so that CI tools like Teamcity won't
    fail the job.

    Args:
        use_warning: Uses a warning log instead of an error.
        iss: The Issue instance.
    """
    if use_warning:
        logger.warning(iss.message, iss)
    else:
        logger.error(iss.message, iss)


def _json_handler(pretty: bool, inst: Any):
    """Use the print function to display the result as json.

    Args:
        pretty: If true, it highlights and indents the json string.
        inst: A python object.
    """
    if inst is not None:
        msg = inst
        if pretty:
            with suppress(Exception):
                msg = highlight_json(json.dumps(inst, indent=2))
        else:
            with suppress(Exception):
                msg = json.dumps(inst, separators=(',', ':'))
        print(msg)  # noqa: WPS421


def _yaml_handler(pretty: bool, inst: Any):
    """Use the print function to display the result as yaml.

    Args:
        pretty: If true, it highlights the yaml string.
        inst: A python object.
    """
    if inst is not None:
        msg = inst
        if pretty:
            with suppress(Exception):
                msg = highlight_yaml(yaml.dumps(inst))
        else:
            with suppress(Exception):
                msg = yaml.dumps(inst)
        print(msg)  # noqa: WPS421


def create_issue_handler(use_warning: bool) -> Callable[[Issue], None]:
    """Generate a function to log an issue.

    Args:
        use_warning: Uses a warning log instead of an error.

    Returns:
        A function that uses the arguments provided.
    """
    return partial(_issue_handler, use_warning)


def create_json_handler(pretty: bool) -> Callable[[Any], None]:
    """Generate a function to display a value to stdout as json.

    Args:
        pretty: If true, it formats with indentation of 2 spaces.

    Returns:
        A function that uses the arguments provided.
    """
    return partial(_json_handler, pretty)


def create_yaml_handler(pretty: bool) -> Callable[[Any], None]:
    """Generate a function to display a value to stdout as yaml.

    Args:
        pretty: If true, it highlights the output.

    Returns:
        A function that uses the arguments provided.
    """
    return partial(_yaml_handler, pretty)


def create_dict_handler(pretty: bool, as_yaml: bool) -> Callable[[Any], None]:
    """Create a json or yaml handler.

    Args:
        pretty: If true, t highlights the output.
        as_yaml: If true, it formats using yaml.

    Returns:
        A function that uses the arguments
    """
    return (
        create_yaml_handler(pretty)
        if as_yaml
        else create_json_handler(pretty)
    )
