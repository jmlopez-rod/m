from typing import Any

from m.cli import Arg, command, validate_json_payload
from pydantic import BaseModel


class Arguments(BaseModel):
    """Format a json payload.

    similar to `python -m json.tool` but instead it uses 2 spaces
    for indentation::

        $ echo '{"a":99}' | m json
        {
          "a": 99
        }

    It is worth noting that if you have access to `jq` or `yq` then
    it should be used instead of `m json`::

        $ echo '{"a":99}' | jq
        {
          "a": 99
        }

    - jq: https://stedolan.github.io/jq/manual/
    - yq: https://mikefarah.gitbook.io/yq/
    """

    payload: Any = Arg(
        default='@-',
        help='json data: @- (stdin), @filename (file), string',
        positional=True,
        validator=validate_json_payload,
    )

    sort_keys: bool = Arg(
        default=False,
        help='sort the output of dictionaries alphabetically by key',
    )


@command(
    help='format json data',
    model=Arguments,
)
def run(arg: Arguments) -> int:
    import json

    from m.color import highlight_json

    json_str = json.dumps(
        arg.payload,
        indent=2,
        sort_keys=arg.sort_keys,
    )
    # Could bypass linter by using run_main but worth doing this
    # especially when we should be using `jq` instead.
    print(highlight_json(json_str))  # noqa: WPS421
    return 0
