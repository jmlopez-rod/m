import sys
import json
import traceback
import inspect
from collections import OrderedDict
from typing import Optional, List, Any, cast
from typing_extensions import TypedDict
from . import fp


IssueDict = TypedDict(
    'IssueDict',
    {
        'message': str,
        'description': str,
        'cause': object,
        'data': object,
        'traceback': List[str]
    },
    total=False,
)


class Issue(Exception):
    """Wrapper to keep track of all exceptions. It provides a 'cause' field
    so that we may know why an issue was triggered."""
    message: str
    description: Optional[str]
    cause: Optional[Exception]
    data: Optional[object]
    include_traceback: bool
    cause_tb: Optional[List[str]]

    def __init__(
        self,
        message: str,
        description: Optional[str] = None,
        cause: Optional[Exception] = None,
        data: Optional[object] = None,
        include_traceback: bool = True
    ):
        """Create an Issue.

        - description: More in depth detail on the issue
        - cause: The exception that or Issue that is responsible for this
                 Issue instance.
        - data: Provide a dictionary with any useful data related to the issue.
        - include_traceback: If False, it skips computing the traceback.
        """
        Exception.__init__(self)
        self.message = message
        self.description = description
        self.cause = cause
        if cause and not isinstance(cause, Issue):
            # https://stackoverflow.com/a/12539332/788553
            try:
                exception_list = [
                    *traceback.format_tb(sys.exc_info()[2]),
                    *traceback.format_exception_only(
                        sys.exc_info()[0],
                        sys.exc_info()[1]),
                ]
                self.cause_tb = [
                    y
                    for x in exception_list
                    for y in x.splitlines()
                ]
            finally:
                pass
        self.data = data
        self.include_traceback = include_traceback
        if self.include_traceback:
            frame = inspect.currentframe()
            try:
                self.traceback = [
                    y
                    for x in traceback.format_stack(frame)[:-1]
                    for y in x.splitlines()
                ]
            finally:
                del frame

    def to_dict(self) -> IssueDict:
        """Convert to a ordered dictionary so that each of the properties are
        written in an expected order.
        """
        obj = cast(IssueDict, OrderedDict())
        obj['message'] = self.message
        if self.description:
            obj['description'] = self.description
        if self.data:
            obj['data'] = self.data
        if self.include_traceback:
            obj['traceback'] = self.traceback
        if self.cause:
            if isinstance(self.cause, Issue):
                obj['cause'] = self.cause.to_dict()
            else:
                obj['cause'] = dict(
                    message=str(self.cause),
                    traceback=self.cause_tb)
        return obj

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def issue(
    message: str,
    description: Optional[str] = None,
    cause: Optional[Exception] = None,
    data: Optional[object] = None,
    include_traceback: bool = True
) -> fp.OneOf[Issue, Any]:
    """Shortcut to create a Bad OneOf containing an Issue."""
    return fp.Bad(Issue(message, description, cause, data, include_traceback))
