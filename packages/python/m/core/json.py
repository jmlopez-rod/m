import json
import sys
from collections.abc import Mapping
from contextlib import suppress
from typing import Any, List
from typing import Mapping as Map
from typing import Optional, Union, cast

from .fp import Good, OneOf
from .io import CITool
from .issue import Issue
from .one_of import issue


def read_json(
    filename: Optional[str],
    error_if_empty: bool = False,
) -> OneOf[Issue, Any]:
    """Return a `Good` containing the parsed contents of the json file."""
    try:
        empty: str = '' if error_if_empty else 'null'
        if filename is None:
            return Good(json.loads(sys.stdin.read() or empty))
        with open(filename, encoding='UTF-8') as file_handle:
            return Good(json.loads(file_handle.read() or empty))
    except Exception as ex:
        return issue(
            'failed to read json file',
            context={'filename': filename or 'SYS.STDIN'},
            cause=ex,
        )


def parse_json(
    data: str,
    error_if_empty: bool = False,
) -> OneOf[Issue, Any]:
    """Return a `Good` containing the parsed contents of the json string."""
    try:
        empty = '' if error_if_empty else 'null'
        return Good(json.loads(data or empty))
    except Exception as ex:
        return issue('failed to parse the json data', cause=ex)


def get(obj: Any, key_str: str) -> OneOf[Issue, Any]:
    """Return the value based on the `key_str` specified. The following
    are equivalent:

    ```
    obj['a']['b']['c'] <=> get(obj, 'a.b.c').value
    ```

    provided that the keys `a`, `b` and `c` are valid. Returns a `Good` if
    the value we want is available, otherwise it returns a `Bad` with the
    path that returned `None`.
    """
    keys = key_str.split('.')
    current = obj
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
            return issue(f'{pth} resulted in an error', cause=ex)
    return Good(current)


def multi_get(
    obj: object,
    *keys: str,
) -> OneOf[Issue, List[Any]]:
    """Call `get` for every input specified by `keys`. It collects the invalid
    keys and returns an `Issue`.

    multi_get(obj, 'a', 'a.b', 'a.b.c')
    """
    result = []
    failures = []
    for key in keys:
        res = get(obj, key)
        if res.is_bad:
            failures.append(
                Issue(
                    message=f'key lookup failure: `{key}`',
                    cause=res.value,
                    include_traceback=False,
                ),
            )
        else:
            result.append(res.value)
    if failures:
        return issue(
            'multi_get key retrieval failure',
            context=[x.to_dict() for x in failures],
            include_traceback=False,
        )
    return Good(result)


def _to_str(obj):
    if isinstance(obj, bool):
        return f'{obj}'.lower()
    if not obj:
        return 'null'
    return f'{obj}'


def jsonq(
    obj: Map[str, Any],
    separator: str,
    display_warning: bool,
    *key_str: str,
) -> int:
    """Print the values obtained from `multi_get` to stdout.

    Returns 0 if all the keys are available. Returns non-zero if there
    are problems.
    """
    result = multi_get(obj, *key_str)
    if result.is_bad:
        val = cast(Issue, result.value)
        if display_warning:
            CITool.warn(val.message)
        else:
            CITool.error(val.message)
        print(result.value, file=sys.stderr)
        return 1
    values = [_to_str(obj) for obj in cast(List[Any], result.value)]
    print(separator.join(values))
    return 0
