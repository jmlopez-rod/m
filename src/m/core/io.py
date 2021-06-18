import sys
import json
from typing import Any, Optional
from .fp import Good, OneOf
from .issue import Issue, issue


def print_problem(msg):
    """Display an error message."""
    print(f'error: {msg}')


def error_block(msg):
    """Display an error block."""
    print(msg)


def read_json(
    filename: Optional[str],
    error_if_empty=False
) -> OneOf[Issue, Any]:
    """Return a `Good` containing the parsed contents of the json file."""
    try:
        empty = '' if error_if_empty else 'null'
        if filename is None:
            return Good(json.loads(sys.stdin.read() or empty))
        return Good(json.loads(open(filename).read() or empty))
    except Exception as ex:
        return issue(
            'failed to read json file',
            data={'filename': filename or 'SYS.STDIN'},
            cause=ex)


def parse_json(data: str, error_if_empty=False) -> OneOf[Issue, Any]:
    """Return a `Good` containing the parsed contents of the json string."""
    try:
        empty = '' if error_if_empty else 'null'
        return Good(json.loads(data or empty))
    except Exception as ex:
        return issue('failed to parse the json data', cause=ex)
