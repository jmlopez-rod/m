import inspect
import json
import sys
import traceback
from collections import OrderedDict
from contextlib import suppress
from typing import cast

from m.color import highlight_json, highlight_yaml
from typing_extensions import TypedDict

from . import yaml

IssueDict = TypedDict(
    'IssueDict',
    {
        'message': str,
        'description': str,
        'cause': object,
        'context': object,
        'traceback': list[str] | str,
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


def _traceback_to_str(traceback_list: list[str]) -> str:
    if not traceback_list:
        return ''
    return '\n'.join([
        '(most recent call last):',
        *traceback_list,
        '',
    ])


# Rule WPS230 is suppressed here since I want to have a flat structure
# with this class. In other places we can refactor and group attributes into
# other classes.
class Issue(Exception):  # noqa: N818, WPS230 - Intention is not to raise
    """Wrapper to keep track of all exceptions.

    It provides a 'cause' field so that we may know why an issue was
    triggered.
    """

    show_traceback = True
    yaml_traceback = True

    message: str
    description: str | None
    cause: Exception | None
    context: object | None
    include_traceback: bool
    cause_tb: list[str] | None
    traceback: list[str] | None

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
                exc_info = sys.exc_info()
                fmt_exception = (
                    traceback.format_exception_only(exc_info[0], exc_info[1])
                    if exc_info[0] is not None and exc_info[1] is not None
                    else []
                )
                exception_list = [
                    *traceback.format_tb(exc_info[2]),
                    *fmt_exception,
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
            if Issue.yaml_traceback and isinstance(self.traceback, list):
                issue_dict['traceback'] = _traceback_to_str(self.traceback)
        if self.cause:
            self._handle_cause(issue_dict)
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
        if Issue.yaml_traceback:
            return yaml.dumps(issue_dict)
        return json.dumps(issue_dict, indent=2)

    def __str__(self) -> str:
        """Convert the instance to a string.

        Returns:
            A string representation of the Issue instance.
        """
        issue_str = self.to_str(Issue.show_traceback)
        if Issue.yaml_traceback:
            return highlight_yaml(issue_str)
        return highlight_json(issue_str)

    def _handle_cause(self, issue_dict: IssueDict) -> None:
        if isinstance(self.cause, Issue):
            issue_dict['cause'] = self.cause.to_dict()
        else:
            issue_dict['cause'] = {
                'message': str(self.cause),
                'traceback': self.cause_tb,
            }
            # I'm clearly assigning to a dict in the above statement...
            # but it is an object so a dict can be assigned to it but that
            # does not mean that we can use `pop` on an object. So we have to
            # help mypy know that know we are dealing with a dict.
            cause = cast(dict, issue_dict['cause'])
            if not self.cause_tb:
                cause.pop('traceback', None)
            if Issue.yaml_traceback and isinstance(self.cause_tb, list):
                cause['traceback'] = _traceback_to_str(self.cause_tb)
