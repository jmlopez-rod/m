import inspect
from ...validators import validate_json_payload
from ...utils import run_main


def add_parser(sub_parser, raw):
    desc = """
        process the output of eslint to determine if the ci process should
        stop.

        examples:

            ~$ eslint [...optons] | m ci eslint
            ...
    """
    parser = sub_parser.add_parser(
        'eslint',
        help='process the json output of eslint',
        formatter_class=raw,
        description=inspect.cleandoc(desc)
    )
    parser.add_argument(
        'payload',
        type=validate_json_payload,
        nargs='?',
        default='@-',
        help='json data: @- (stdin), @filename (file), string. Defaults to @-'
    )
    parser.add_argument(
        '-c',
        '--config',
        required=True,
        type=validate_json_payload,
        help='config data: @filename (file), string.'
    )


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....ci.eslint import eslint
    return run_main(lambda: eslint(arg.payload, arg.config), print)
