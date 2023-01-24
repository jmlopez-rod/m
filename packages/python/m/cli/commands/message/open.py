from m.cli import command
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Open a block to group several messages in the build log."""

    name: str = Field(
        description='block name to open',
        positional=True,
        required=True,
    )
    description: str = Field(
        description='block description',
        positional=True,
        required=True,
    )


@command(
    name='open',
    help='open a block',
    model=Arguments,
)
def run(arg: Arguments):
    from m.core.ci_tools import get_ci_tool
    get_ci_tool().open_block(arg.name, arg.description)
    return 0
