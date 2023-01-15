from typing import Any

from pydantic import BaseModel, Field

from ..argparse import add_model, cli_options
from ..validators import validate_json_payload


class Arguments(BaseModel):
    """Format a json payload.

        $ echo '{"a":99}' | m json
        {
          "a": 99
        }

    similar to `python -m json.tool` but instead it uses 2 spaces
    for indentation.

    It is worth noting that if you have access to `jq` or `yq` then
    it should be used instead of `m json`.

        $ echo '{"a":99}' | jq
        {
          "a": 99
        }

    - jq: https://stedolan.github.io/jq/manual/
    - yq: https://mikefarah.gitbook.io/yq/
    """  # noqa

    payload: Any | None = Field(
        '@-',
        description='json data: @- (stdin), @filename (file), string',
        validator=validate_json_payload,
        positional=True,
    )

    sort_keys: bool = Field(
        False,
        description='sort the output of dictionaries alphabetically by key',
    )


def add_parser(sub_parser, _raw):
    parser = sub_parser.add_parser('json', help='format json data')
    add_model(parser, Arguments)


def run(arg):
    # pylint: disable=import-outside-toplevel
    import json
    import sys

    opt = cli_options(Arguments, arg)
    json.dump(opt.payload, sys.stdout, indent=2, sort_keys=opt.sort_keys)
    sys.stdout.write('\n')
    return 0
