import sys
from argparse import ArgumentTypeError
from pathlib import Path

from ..core.json import parse_json, read_json


def validate_json_payload(file_path: str):
    """Return a dictionary from the contents of file_path.

    This is a string that tell us to read from a file, stdin or just
    plain json data.
    """
    if file_path == '@-':
        res = read_json(None)
        if res.is_bad:
            msg = f'invalid json payload in SYS.STDIN\n{res.value}'
            raise ArgumentTypeError(msg)
        return res.value
    if file_path.startswith('@'):
        filename = file_path[1:]
        if not Path(filename).exists():
            raise ArgumentTypeError(f'file "{filename}" does not exist')
        res = read_json(filename)
        if res.is_bad:
            raise ArgumentTypeError(f'invalid json payload in {filename}')
        return res.value
    res = parse_json(file_path)
    if res.is_bad:
        raise ArgumentTypeError(f'invalid json payload\n{res.value}')
    return res.value


def validate_payload(file_path: str) -> str:
    """Return the raw payload.

    This allows us to read from a file or the stdin stream.
    """
    if file_path.startswith(r'\@'):
        # escape @ with \ to let the cli know that the payload starts with @
        return file_path[1:]
    if file_path == '@-':
        return sys.stdin.read()
    if file_path.startswith('@'):
        filename = file_path[1:]
        if not Path(filename).exists():
            raise ArgumentTypeError(f'file "{filename}" does not exist')
        with open(filename, encoding='UTF-8') as fp:
            return fp.read()
    return file_path


def validate_non_empty_str(value):
    """Return the value as long as its not empty."""
    if not value:
        raise ArgumentTypeError('empty value not allowed')
    return value
