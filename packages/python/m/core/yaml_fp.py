from pathlib import Path
from typing import Any, Callable

import yaml

from . import rw
from .issue import Issue
from .json import parse_json
from .one_of import Good, OneOf, issue, one_of

ParserFunction = Callable[[str, bool], OneOf[Issue, Any]]


def parse_yaml(
    yaml_str: str,
    error_if_empty: bool = False,
) -> OneOf[Issue, Any]:
    """Parse a string as yaml.

    Args:
        yaml_str: The string to parse.
        error_if_empty: The parser may throw an error if `True`.

    Returns:
        A `Good` containing the parsed contents of the yaml string.
    """
    empty = '' if error_if_empty else 'null'
    try:
        return Good(yaml.safe_load(yaml_str or empty))
    except Exception as ex:
        return issue('failed to parse the yaml data', cause=ex)


def read_yson(
    filename: str,
    error_if_empty: bool = False,
) -> OneOf[Issue, Any]:
    """Read a json object from a json or yaml file.

    It will choose the parser based on the filename extension.

    Args:
        filename: The filename to read from, if `None` it reads from stdin.
        error_if_empty: The json parser may throw an error if `True`.

    Returns:
        A `Good` containing the parsed contents of the json file.
    """
    empty: str = '' if error_if_empty else 'null'
    file_map: dict[str, ParserFunction] = {
        '.yaml': parse_yaml,
        '.yml': parse_yaml,
        '.json': parse_json,
    }
    ext = Path(filename).suffix
    parser = file_map.get(ext, parse_json)
    return one_of(lambda: [
        json_data
        for json_str in rw.read_file(filename)
        for json_data in parser(json_str or empty, error_if_empty)
    ]).flat_map_bad(
        lambda err: issue(
            f'failed to read "{ext}" file',
            cause=err,
            context={'filename': filename or 'SYS.STDIN'},
        ),
    )
