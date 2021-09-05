import inspect

from ..validators import validate_json_payload


def add_parser(sub_parser, raw):
    desc = """
        Format a json payload.

            $ echo '{"a":99}' | m json
            {
              "a": 99
            }

        similar to `python -m json.tool` but instead it uses 2 spaces
        for indentation.
    """
    parser = sub_parser.add_parser(
        'json',
        help='format json data',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )
    parser.add_argument(
        'payload',
        type=validate_json_payload,
        nargs='?',
        default='@-',
        help='json data: @- (stdin), @filename (file), string. Defaults to @-',
    )
    parser.add_argument(
        '--sort-keys',
        action='store_true',
        default=False,
        help='sort the output of dictionaries alphabetically by key',
    )


def run(arg):
    # pylint: disable=import-outside-toplevel
    import json
    import sys
    json.dump(arg.payload, sys.stdout, indent=2, sort_keys=arg.sort_keys)
    sys.stdout.write('\n')
