import sys
from argparse import ArgumentTypeError
from pathlib import Path

from ..core.json import parse_json, read_json
from ..core.yaml_fp import read_yson


def validate_json_payload(file_path: str):
    """Return a dictionary from the contents of file_path.

    This is a string that tell us to read from a file, stdin or just
    plain json data.

    It can be used parse `yaml` files as well. The extension should be
    `.yaml` or `.yml`.

    Args:
        file_path: A string with the json payload. If it starts with `@` then
            the name of a valid json file from where the payload will be read.

    Raises:
        ArgumentTypeError: If the file_path is meant to be a valid path and it
            does not exist.

    Returns:
        A parsed json payload
    """
    if file_path == '@-':
        res = read_json(None)
        if res.is_bad:
            msg = f'invalid json payload in SYS.STDIN\n{res.value}'
            raise ArgumentTypeError(msg)
        return res.value
    if file_path.startswith('@'):
        err = ''
        filename = file_path[1:]
        if Path.exists(Path(filename)):
            res = read_yson(filename)
            if not res.is_bad:
                return res.value
            err = f'invalid json payload in {filename}\n{res.value}'
        else:
            err = f'file "{filename}" does not exist'
        if err:
            raise ArgumentTypeError(err)
    res = parse_json(file_path)
    if res.is_bad:
        raise ArgumentTypeError(f'invalid json payload\n{res.value}')
    return res.value


def validate_payload(file_path: str) -> str:
    """Return the raw payload.

    This allows us to read from a file or the stdin stream.

    Args:
        file_path: A string with the payload. If it starts with `@` then the
            name of a valid file from where the payload will be read.

    Raises:
        ArgumentTypeError: If the file_path is meant to be a valid path and it
            does not exist.

    Returns:
        The payload found in the file.
    """
    if file_path.startswith(r'\@'):
        # escape @ with \ to let the cli know that the payload starts with @
        return file_path[1:]
    if file_path == '@-':
        return sys.stdin.read()
    if file_path.startswith('@'):
        filename = file_path[1:]
        path_handle = Path(filename)
        if not Path.exists(path_handle):
            raise ArgumentTypeError(f'file "{filename}" does not exist')
        with Path.open(path_handle, encoding='UTF-8') as fp:
            return fp.read()
    return file_path


def validate_non_empty_str(arg_value: str) -> str:
    """Return the value as long as its not empty.

    Args:
        arg_value: The input provided by argparse.

    Raises:
        ArgumentTypeError: If the input is not provided.

    Returns:
        The value if non empty.
    """
    if not arg_value:
        raise ArgumentTypeError('empty value not allowed')
    return arg_value
