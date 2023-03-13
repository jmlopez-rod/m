import json
from collections.abc import Mapping
from contextlib import suppress
from typing import Any
from typing import Mapping as Map
from typing import Union

from . import rw
from .fp import Good, OneOf
from .issue import Issue
from .one_of import issue, one_of


def read_json(
    filename: str | None,
    error_if_empty: bool = False,
) -> OneOf[Issue, Any]:
    """Read a json object from a json file.

    Args:
        filename: The filename to read from, if `None` it reads from stdin.
        error_if_empty: The json parser may throw an error if `True`.

    Returns:
        A `Good` containing the parsed contents of the json file.
    """
    empty: str = '' if error_if_empty else 'null'
    return one_of(lambda: [
        json_data
        for json_str in rw.read_file(filename)
        for json_data in parse_json(json_str or empty, error_if_empty)
    ]).flat_map_bad(
        lambda err: issue(
            'failed to read json file',
            cause=err,
            context={'filename': filename or 'SYS.STDIN'},
        ),
    )


def parse_json(
    json_str: str,
    error_if_empty: bool = False,
) -> OneOf[Issue, Any]:
    """Parse a string as json.

    Args:
        json_str: The string to parse.
        error_if_empty: The json parser may throw an error if `True`.

    Returns:
        A `Good` containing the parsed contents of the json string.
    """
    empty = '' if error_if_empty else 'null'
    try:
        return Good(json.loads(json_str or empty))
    except Exception as ex:
        return issue('failed to parse the json data', cause=ex)


def get(dict_inst: Any, key_str: str) -> OneOf[Issue, Any]:
    """Return the value based on the `key_str` specified.

    The following are equivalent::

        obj['a']['b']['c'] <=> get(obj, 'a.b.c').value

    provided that the keys `a`, `b` and `c` are valid.

    Args:
        dict_inst: The dictionary instance to query.
        key_str: A simple query to fetch from the dict_inst.

    Returns:
        A `Good` if the value we want is available, otherwise it returns a
        `Bad` with the path that returned `None`.
    """
    keys = key_str.split('.')
    current = dict_inst
    for num, key in enumerate(keys):
        new_key: Union[str, int] = key
        with suppress(ValueError):
            new_key = int(key)
        try:
            current = current[new_key]
        except KeyError:
            pth = '.'.join(keys[:num + 1])
            return issue(f'`{pth}` path was not found')
        except Exception as ex:
            pth = '.'.join(keys[:num])
            if not isinstance(current, Mapping):
                context = pth or current
                return issue(f'`{context}` is not a dict')
            # catch unknown issue
            return issue(  # pragma: no cover
                f'{pth} resulted in an error',
                cause=ex,
            )
    return Good(current)


def multi_get(
    dict_inst: object,
    *keys: str,
) -> OneOf[Issue, list[Any]]:
    """Call `get` for every input specified by `keys`.

    It collects the invalid keys and returns an `Issue`::

        multi_get(obj, 'a', 'a.b', 'a.b.c')

    Args:
        dict_inst: The dictionary instance to query.
        keys: The queries to apply.

    Returns:
        A `Good` with a list of the results if successful, otherwise a `Bad`
        with the list of failures.
    """
    result_items = []
    failures = []
    for key in keys:
        res = get(dict_inst, key)
        if res.is_bad:
            failures.append(
                Issue(
                    message=f'key lookup failure: `{key}`',
                    cause=res.value,
                    include_traceback=False,
                ),
            )
        else:
            result_items.append(res.value)
    if failures:
        return issue(
            'multi_get key retrieval failure',
            context=[x.to_dict() for x in failures],
            include_traceback=False,
        )
    return Good(result_items)


def _to_str(inst: Any):
    if isinstance(inst, bool):
        return f'{inst}'.lower()
    if inst is None:
        return 'null'
    return f'{inst}'


def jsonq(
    dict_inst: Map[str, Any],
    separator: str,
    *key_str: str,
) -> OneOf[Issue, str]:
    """Stringify the values obtained from `multi_get`.

    Args:
        dict_inst: The dictionary instance to query.
        separator: A string to use to separate the results.
        key_str: The queries to apply.

    Returns:
        A string separated by `separator` if successful or an Issue with
        a description of the problems.
    """
    return one_of(lambda: [
        separator.join(map(_to_str, key_values))
        for key_values in multi_get(dict_inst, *key_str)
    ])
