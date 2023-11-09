import sys
from pathlib import Path

from .one_of import Good, Issue, OneOf, issue, one_of


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


def write_file(filename: str, text: str, mode: str = 'w') -> OneOf[Issue, int]:
    """Write contents to a file in a functional programming style.

    Args:
        filename: The file path where contents will be written.
        text: The contents of the file.
        mode: The mode to open the file in.

    Returns:
        A `Good` containing 0 if the file was written.
    """
    try:
        with Path.open(Path(filename), mode, encoding='UTF-8') as fp:
            fp.write(text)
    except Exception as ex:
        return issue(
            'failed to write file',
            context={'filename': filename},
            cause=ex,
        )
    return Good(0)


def assert_file_exists(path: str) -> OneOf[Issue, Path]:
    """Assert that a file exists.

    Args:
        path: The path to the file.

    Returns:
        A `Good` containing the `Path` if the file exists.
    """
    path_inst = Path(path)
    if path_inst.exists():
        return Good(path_inst)
    return issue('file does not exist', context={'path': path})


def _insert_to_file(
    file_content: str,
    start: str,
    text: str,
    end: str,
) -> OneOf[Issue, str]:
    first_split = file_content.split(start)
    left_content = first_split[0]
    right_content = ''
    if len(first_split) > 1:
        second_split = first_split[-1].split(end)
        right_content = second_split[-1]
    file_data = [left_content, start, text, end, right_content]
    return Good(''.join(file_data))


def insert_to_file(
    filename: str,
    start: str,
    text: str,
    end: str,
) -> OneOf[Issue, int]:
    """Insert content to a file.

    Args:
        filename: The file to insert to.
        start: The start delimiter where the insertion will take place.
        text: The main content to insert.
        end: The end delimiter.

    Returns:
        None if successful, else an issue.
    """
    return one_of(lambda: [
        0
        for file_content in read_file(filename)
        for new_content in _insert_to_file(file_content, start, text, end)
        for _ in write_file(filename, new_content)
    ])
