import inspect

from ..validators import validate_json_payload


def add_parser(sub_parser, raw):
    desc = r"""
        query json data.

        single value:

            m jsonq path.to.property < file.json
            cat file.json | m jsonq path.to.property
            m jsonq @file.json path.to.property

        Return the value stored in the json file. For arrays and objects it
        will print the python representation of the object.

        multiple values:

            m jsonq path1 path2 path3 < file.json
            cat file.json | m jsonq path1 path2 path3
            m jsonq @file.json path1 path2 path3

        use `read` to store in bash variables:

            read -r -d '\n' \
                var1 var2 var3 \
                <<< "$(m jsonq @file.json 'path1' 'path2' 'path3')"
    """
    parser = sub_parser.add_parser(
        'jsonq',
        help='query json data',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )
    add = parser.add_argument
    add(
        'payload',
        type=validate_json_payload,
        nargs='?',
        default='@-',
        help='json data: @- (default stdin), @filename (file), string',
    )
    add(
        '-w',
        '--warn',
        action='store_true',
        help='print warning messages instead of errors',
    )
    add(
        '-s',
        '--separator',
        type=str,
        default='\n',
        help=r'separator for multiple values (default \n)',
    )
    add('query', type=str, nargs='+', help='path to json data')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ...core.json import jsonq
    return jsonq(arg.payload, arg.separator, arg.warn, *arg.query)
