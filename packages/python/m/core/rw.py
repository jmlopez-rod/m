import sys
from pathlib import Path

from .one_of import Good, Issue, OneOf, issue


def read_file(filename: str | None) -> OneOf[Issue, str]:
    """FP version of open to read the contents of a file.

    If `None` is provided it will attempt to read from `sys.stdin`.

    Args:
        filename: The file path to read.

    Returns:
        A `Good` containing the contents of the file.
    """
    if filename is None:
        return Good(sys.stdin.read())
    try:
        with Path.open(Path(filename), encoding='UTF-8') as fp:
            return Good(fp.read())
    except Exception as ex:
        return issue(
            'failed to read file',
            context={'filename': filename},
            cause=ex,
        )


def write_file(filename: str, text: str) -> OneOf[Issue, int]:
    """FP version of open to write to a file.

    Args:
        filename: The file path where contents will be written.
        text: The contents of the file.

    Returns:
        A `Good` containing 0 if the file was written.
    """
    try:
        with Path.open(Path(filename), 'w', encoding='UTF-8') as fp:
            fp.write(text)
    except Exception as ex:
        return issue(
            'failed to write file',
            context={'filename': filename},
            cause=ex,
        )
    return Good(0)
