import inspect


def add_parser(sub_parser, raw):
    desc = """
        report an warning

        example:

            ~$ m message warn 'this is a warning' -f app.js -l 1 -c 5
            ::warning file=app.js,line=1,col=5::Missing semicolon
    """
    parser = sub_parser.add_parser(
        'warn',
        help='report a warning',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )
    add = parser.add_argument
    add('message', type=str, help='warning message')
    add('-f', '--file', type=str, help='filename where warning occurred')
    add('-l', '--line', type=str, help='line where warning occurred')
    add('-c', '--col', type=str, help='column where warning occurred')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....core.io import CiTool
    CiTool.warn(arg.message, arg.file, arg.line, arg.col)
    return 0
