import inspect


def add_parser(sub_parser, raw):
    desc = 'open a block to group several messages in the build log'
    parser = sub_parser.add_parser(
        'open',
        help='open block',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )
    parser.add_argument('name', type=str, help='block name to open')
    parser.add_argument('description', type=str, help='block description')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....core.io import CiTool
    CiTool.open_block(arg.name, arg.description)
    return 0
