from m.cli import Arg, BaseModel, command


class Arguments(BaseModel):
    """Open a block to group several messages in the build log."""

    name: str = Arg(
        help='block name to open',
        positional=True,
        required=True,
    )
    description: str = Arg(
        help='block description',
        positional=True,
        required=True,
    )


@command(
    help='open a block',
    model=Arguments,
)
def run(arg: Arguments):
    from m.log import Logger

    logger = Logger('m.cli')
    logger.open_block(arg.name, arg.description)
    return 0
