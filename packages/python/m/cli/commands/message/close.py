from m.cli import command
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Close a block.

    When a block is closed, all its inner blocks are closed automatically.
    Not all CI Tools support nesting.
    """

    name: str = Field(
        description='block name to close',
        positional=True,
        required=True,
    )


@command(
    name='close',
    help='close a block',
    model=Arguments,
)
def run(arg: Arguments):
    from m.core.ci_tools import get_ci_tool
    get_ci_tool().close_block(arg.name)
    return 0
