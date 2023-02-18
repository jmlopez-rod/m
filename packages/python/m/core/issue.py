import inspect
import json
import sys
import traceback
from collections import OrderedDict
from contextlib import suppress
from typing import cast

from typing_extensions import TypedDict

IssueDict = TypedDict(
    'IssueDict',
    {
        'message': str,
        'description': str,
        'cause': object,
        'context': object,
        'traceback': list[str],
    },
    total=False,
)


def remove_traceback(issue_dict: object) -> None:
    """Remove the `traceback` key from a dictionary if it exists.

    It will recursively remove the `traceback` from its cause or context.

    Args:
        issue_dict: A dictionary representation of an `Issue`.
    """
    if isinstance(issue_dict, dict):
        if 'traceback' in issue_dict:
            issue_dict.pop('traceback')
        cause = issue_dict.get('cause')
        if cause:
            remove_traceback(cause)
        context = issue_dict.get('context')
        remove_traceback(context)
        if isinstance(context, list):
            for context_item in context:
                remove_traceback(context_item)


# Rule WPS230 is suppressed here since I want to have a flat structure
# with this class. In other places we can refactor and group attributes into
# other classes.
class Issue(Exception):  # noqa: N818, WPS230 - Intention is not to raise
    """Wrapper to keep track of all exceptions.

    It provides a 'cause' field so that we may know why an issue was
    triggered.
    """

    show_traceback = True

    message: str
    description: str | None
    cause: Exception | None
    context: object | None
    include_traceback: bool
    cause_tb: list[str] | None

    def __init__(  # noqa: WPS211 - need to initialize the attributes
        self,
        message: str,
        description: str | None = None,
        cause: Exception | None = None,
        context: object | None = None,
        include_traceback: bool = True,
    ):
        """Create an Issue.

        Args:
            message: Simple description of the issue.
            description: More in depth detail on the issue
            cause: The exception/Issue that is responsible for this instance.
            context: Dictionary with any useful data related to the issue.
            include_traceback: If False, it skips computing the traceback.
        """
        super().__init__()
        self.message = message
        self.description = description
        self.cause = cause
        if cause and not isinstance(cause, Issue):
            # https://stackoverflow.com/a/12539332/788553
            with suppress(BaseException):
                exception_list = [
                    *traceback.format_tb(sys.exc_info()[2]),
                    *traceback.format_exception_only(
                        sys.exc_info()[0],
                        sys.exc_info()[1],
                    ),
                ]
                self.cause_tb = [
                    y
                    for x in exception_list
                    for y in x.splitlines()
                ]
        self.context = context
        self.include_traceback = include_traceback
        self.traceback = None
        if self.include_traceback:
            frame = inspect.currentframe()
            self.traceback = [
                y
                for x in traceback.format_stack(frame)[:-1]
                for y in x.splitlines()
            ]

    def only_context(self) -> bool:
        """Return true if the issue only offers context.

        In some cases we may create an issue with only a message and a
        context. This function will let us know of such case so that a
        log formatter may be able to unwrap the context.

        Returns:
            True if it is safe to only display the context value on a log.
        """
        has_context = self.context is not None
        all_props = (self.description, self.traceback, self.cause)
        return has_context and not [_ for _ in all_props if _]

    def to_dict(self, show_traceback: bool = True) -> IssueDict:
        """Convert to a ordered dictionary.

        This is done so that each of the properties are written in an expected
        order.

        Args:
            show_traceback: If False, it will remove all stacktraces.

        Returns:
            An `IssueDict` instance.
        """
        issue_dict = cast(IssueDict, OrderedDict())
        issue_dict['message'] = self.message
        if self.description:
            issue_dict['description'] = self.description
        if self.context:
            issue_dict['context'] = self.context
        if self.include_traceback and self.traceback:
            issue_dict['traceback'] = self.traceback
        if self.cause:
            if isinstance(self.cause, Issue):
                issue_dict['cause'] = self.cause.to_dict()
            else:
                issue_dict['cause'] = {
                    'message': str(self.cause),
                    'traceback': self.cause_tb,
                }
        if not show_traceback:
            remove_traceback(issue_dict)
        return issue_dict

    def to_str(self, show_traceback: bool) -> str:
        """Convert the instance to string.

        Args:
            show_traceback: If false, it will remove the error traceback.

        Returns:
            A string representation of the Issue instance.
        """
        issue_dict = self.to_dict(show_traceback=show_traceback)
        return json.dumps(issue_dict, indent=2)

    def __str__(self) -> str:
        """Convert the instance to a string.

        Returns:
            A string representation of the Issue instance.
        """
        return self.to_str(Issue.show_traceback)
