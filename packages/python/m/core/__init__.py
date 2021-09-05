from typing import Any, cast, Callable, List, Optional
from .issue import Issue
from .fp import OneOf, Good, Bad, StopBadIteration, G


def issue(
    message: str,
    description: Optional[str] = None,
    cause: Optional[Exception] = None,
    data: Optional[object] = None,
    include_traceback: bool = True,
) -> OneOf[Issue, Any]:
    """Shortcut to create a Bad OneOf containing an Issue."""
    return Bad(Issue(message, description, cause, data, include_traceback))


def one_of(comp: Callable[[], List[G]]) -> OneOf[Any, G]:
    """`comp` should be a lambda function which returns an array with a single
    value. To be used so that we may iterate over OneOf objects that may raise
    the StopBadIteration exception.
    """
    try:
        return Good(comp()[0])
    except StopBadIteration as ex:
        return cast(Bad, ex.bad)
    except BaseException as ex:
        return issue('one_of caught exception', cause=cast(Exception, ex))
