import inspect


def add_parser(sub_parser, raw):
    desc = """
        report an error

        example:

            ~$ m message error 'this is an error'
            ::error::this is an error
            ~$ echo $?
            1

        The procedure exits with non-zero code.
    """
    parser = sub_parser.add_parser(
        'error',
        help='report an error',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )
    add = parser.add_argument
    add('message', type=str, help='error message')
    add('-f', '--file', type=str, help='filename where error occurred')
    add('-l', '--line', type=str, help='line where error occurred')
    add('-c', '--col', type=str, help='column where error occurred')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....core.io import CiTool
    CiTool.error(arg.message, arg.file, arg.line, arg.col)
    return 1
