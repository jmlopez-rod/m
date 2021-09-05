import inspect


def add_parser(sub_parser, raw):
    desc = """
        close a block. When a block is closed, all its inner blocks are
        closed automatically. Note: Not all CI Tools support nesting.
    """
    parser = sub_parser.add_parser(
        'close',
        help='close block',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )
    parser.add_argument('name', type=str, help='block name to close')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....core.io import CiTool
    CiTool.close_block(arg.name)
    return 0
