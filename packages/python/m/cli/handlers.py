
import json
from contextlib import suppress
from functools import partial
from typing import Any, Callable

from m.core import Issue
from m.log import Logger

logger = Logger('m.cli.cli_helpers')


def _issue_handler(use_warning: bool, iss: Issue):
    """Log an Issue instance.

    Provides a few options on how to log it. For instance, we may want to
    log as a warning to avoid CI tools such as Teamcity from failing the
    job.

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
        pretty: If true, it formats with indentation of 2 spaces.
        inst: A python object.
    """
    if inst is not None:
        msg = inst
        if pretty:
            with suppress(Exception):
                msg = json.dumps(inst, indent=2)
        else:
            with suppress(Exception):
                msg = json.dumps(inst, separators=(',', ':'))
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
