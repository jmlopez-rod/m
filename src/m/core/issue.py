import sys
import json
import traceback
import inspect
from collections import OrderedDict
from .fp import Bad


class Issue(Exception):
    """Wrapper to keep track of all exceptions. It provides a 'cause' field
    so that we may know why an issue was triggered."""

    def __init__(self, message, **kwargs):
        """Create an Issue. The available keyword arguments are:

        - description: More in depth detail on the issue
        - cause: The exception that or Issue that is responsible for this
                 Issue instance.
        - data: Provide a dictionary with any useful data related to the issue.
        - include_traceback: If False, it skips computing the traceback.
        """
        Exception.__init__(self)
        self.message = message
        self.description = kwargs.get('description')
        cause = kwargs.get('cause')
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
        self.data = kwargs.get('data')
        self.include_traceback = kwargs.get('include_traceback', True)
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

    def to_dict(self):
        """Convert to a ordered dictionary so that each of the properties are
        written in an expected order.
        """
        obj = OrderedDict([('message', self.message)])
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

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)


def issue(message: str, **kwargs):
    """Shortcut to create a Bad OneOf containing an Issue."""
    return Bad(Issue(message, **kwargs))
