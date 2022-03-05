from inspect import cleandoc as cdoc
from typing import Tuple

from ..argparse import STORE_TRUE, Arg, add_arguments
from ..validators import validate_json_payload

DESC = """
    Format a json payload.

        $ echo '{"a":99}' | m json
        {
            "a": 99
        }

    similar to `python -m json.tool` but instead it uses 2 spaces
    for indentation.
"""
ARGS: Tuple[Arg, ...] = (
    (
        ['payload'],
        'json data: @- (stdin), @filename (file), string. Defaults to @-',
        {'type': validate_json_payload, 'nargs': '?', 'default': '@-'},
    ),
    (
        ['--sort-keys'],
        'sort the output of dictionaries alphabetically by key',
        {**STORE_TRUE},
    ),
)


def add_parser(sub_parser, raw):
    parser = sub_parser.add_parser(
        'json',
        help='format json data',
        formatter_class=raw,
        description=cdoc(DESC),
    )
    add_arguments(parser, ARGS)


def run(arg):
    # pylint: disable=import-outside-toplevel
    import json
    import sys
    json.dump(arg.payload, sys.stdout, indent=2, sort_keys=arg.sort_keys)
    sys.stdout.write('\n')
    return 0
