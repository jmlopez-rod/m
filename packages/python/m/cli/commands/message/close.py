from m.cli import Arg, BaseModel, command


class Arguments(BaseModel):
    """Close a block.

    When a block is closed, all its inner blocks are closed automatically.
    Not all CI Tools support nesting.
    """

    name: str = Arg(
        help='block name to close',
        positional=True,
        required=True,
    )


@command(
    help='close a block',
    model=Arguments,
)
def run(arg: Arguments):
    from m.log import Logger

    logger = Logger('m.cli')
    logger.close_block(arg.name)
    return 0
