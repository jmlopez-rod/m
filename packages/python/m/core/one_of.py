from typing import Any, Callable, TypeVar, cast

from pydantic import ValidationError

from .fp import Bad, Good, OneOf, StopBadIteration
from .issue import Issue

G = TypeVar('G')  # pylint: disable=invalid-name


def issue(  # noqa: WPS211
    message: str,
    description: str | None = None,
    cause: Exception | None = None,
    context: object | None = None,
    include_traceback: bool = True,
) -> OneOf[Issue, Any]:
    """Shortcut to create a Bad OneOf containing an Issue.

    Args:
        message: The issue message.
        description: Optional description.
        cause: Optional exception that caused the issue.
        context: Optional dictionary to provide extra information.
        include_traceback: Defaults to true to provide the stack trace.

    Returns:
        An instance of an `Issue`.
    """
    inst = Issue(message, description, cause, context, include_traceback)
    return Bad(inst)


def one_of(comp: Callable[[], list[G]]) -> OneOf[Any, G]:
    """Handle the "Good" value of a `OneOf`.

    To be used so that we may iterate over OneOf objects that may raise
    the `StopBadIteration` exception.

    Args:
        comp: A lambda function returning an array with a single value.

    Returns:
        A `OneOf` with the value returned from `comp`.
    """
    res = None
    try:
        res = comp()
    except StopBadIteration as ex:
        return cast(Bad, ex.bad)
    except ValidationError as ex:
        return issue('pydantic validation error', cause=ex)
    except Exception as ex:
        return issue('one_of caught exception', cause=ex)
    if res:
        return Good(res[0])
    # LOOK AT ME - you may be here because a mock is not returning a OneOf.
    return issue('one_of empty response - iteration missing a OneOf')


def to_one_of(
    callback: Callable[[], Any],
    message: str,
    context: object | None = None,
) -> OneOf[Issue, int]:
    """Wrap a python call in a `OneOf`.

    Args:
        callback: A lambda function with a simple python statement.
        message: An error message in case the statement raises an exception.
        context: Additional error context.

    Returns:
        A `OneOf` containing an `Issue` if the callback raises an error.
    """
    try:
        callback()
    except Exception as ex:
        return issue(message, cause=ex, context=context)
    return Good(0)


def non_issue(inst: OneOf[Issue, G]) -> G:
    """Obtain the value of the `OneOf` as if it was a Good value.

    Warning: This should only be used provided that we know for sure
    that we are not dealing with a `Bad` value.

    Args:
        inst: A OneOf.

    Returns:
        The value stored in the OneOf.
    """
    # The assert statement can go away with the -O flag.
    assert not inst.is_bad  # noqa: S101
    return cast(G, inst.value)
