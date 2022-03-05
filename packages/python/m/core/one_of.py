from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

from .fp import Bad, Good, OneOf, StopBadIteration
from .issue import Issue

G = TypeVar('G')  # pylint: disable=invalid-name


def issue(  # noqa: WPS211
    message: str,
    description: Optional[str] = None,
    cause: Optional[Exception] = None,
    context: Optional[object] = None,
    data: Optional[object] = None,  # noqa: WPS110
    include_traceback: bool = True,
) -> OneOf[Issue, Any]:
    """Shortcut to create a Bad OneOf containing an Issue.

    Args:
        message: The issue message.
        description: Optional description.
        cause: Optional exception that caused the issue.
        context: Optional dictionary to provide extra information.
        data: deprecated, use context instead.
        include_traceback: Defaults to true to provde the stack trace.

    Returns:
        An instance of an `Issue`.
    """
    return Bad(
        Issue(message, description, cause, context or data, include_traceback),
    )


def one_of(comp: Callable[[], List[G]]) -> OneOf[Any, G]:
    """Handle the "Good" value of a `OneOf`.

    To be used so that we may iterate over OneOf objects that may raise
    the `StopBadIteration` exception.

    Args:
        comp: A lambda function returning an array with a single value.

    Returns:
        A `OneOf` with the value returned from `comp`.
    """
    try:
        return Good(comp()[0])
    except StopBadIteration as ex:
        return cast(Bad, ex.bad)
    except Exception as ex:
        return issue('one_of caught exception', cause=ex)


def to_one_of(
    callback: Callable[[], Any],
    message: str,
    context: Optional[Dict[str, Any]] = None,
) -> OneOf[Issue, int]:
    """Wrap a python call in a `OneOf`.

    Args:
        callback: A lambda function with a simple python statement.py
        message: An error message in case the statment raises an exception.
        context: Additional error context.

    Returns:
        A `OneOf` containing an `Issue` if the callback raises an error.
    """
    try:
        callback()
    except Exception as ex:
        return issue(message, cause=ex, context=context)
    return Good(0)
