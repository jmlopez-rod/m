import json
import logging
import textwrap
from typing import cast

from m.core import Issue


def indent_payload(
    indent: int,
    payload: dict,
    prepend_new_line: bool = True,
) -> str:
    """Stringify a dictionary as JSON and indent it.

    Args:
        indent: The number of spaces to indent.
        payload: The data to stringify and indent.
        prepend_new_line: Prepend a new line to the payload if `True`.

    Returns:
        An indented payload.
    """
    json_dict = json.dumps(payload, indent=2)
    indented_payload = textwrap.indent(json_dict, ' ' * indent)
    return f'\n{indented_payload}' if prepend_new_line else indented_payload


def format_context(
    record: logging.LogRecord,
    indent: int,
    show_traceback: bool,
) -> str:
    """Extract the context from a log record.

    Args:
        record: The log record instance.
        indent: The level of indentation to apply to the string.
        show_traceback: Attempts to display the traceback if it exists.

    Returns:
        A string with leading new line of the context associated with a log
        record.
    """
    context = record.__dict__.get('context')
    data_dict = None
    if isinstance(context, Issue):
        data_dict = cast(dict, context.to_dict(show_traceback=show_traceback))
        if context.only_context():
            data_dict = data_dict['context']
    else:
        data_dict = context
    return indent_payload(indent, data_dict) if data_dict else ''


def format_location(parts: list[str | None]) -> str:
    """Join a list of possible defined strings.

    Args:
        parts: A list of possibly defined strings.

    Returns:
        A string with the location or an empty string.
    """
    loc = ':'.join([x for x in parts if x])
    return f'[{loc}]' if loc else ''


def default_record_fmt(
    record: logging.LogRecord,
    asctime: str,
    after_time: str,
    after_msg: str,
) -> str:
    """Format a log record.

    Args:
        record: A log record.
        asctime: The string representing the time of creation.
        after_time: A string that will be placed after the time.
        after_msg: A string to be placed after the main message.

    Returns:
        A formatted string.
    """
    fmt_time = f'[{asctime}]' if asctime else ''
    prefix = f'[{record.levelname}] {fmt_time}{after_time}'.rstrip()
    return f'{prefix}: {record.msg}{after_msg}'
