from m.cli import Arg, BaseModel, command


class Arguments(BaseModel):
    """Close and immediately open another block."""

    to_close: str = Arg(
        help='block name to close',
        positional=True,
        required=True,
    )
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
    help='close and open a sibling block',
    model=Arguments,
)
def run(arg: Arguments):
    from m.log import Logger

    logger = Logger('m.cli')
    logger.close_block(arg.to_close)
    logger.open_block(arg.name, arg.description)
    return 0
