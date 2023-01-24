from m.cli import command
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Close and immediately open another block."""

    to_close: str = Field(
        description='block name to close',
        positional=True,
        required=True,
    )
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
    name='sibling_block',
    help='close and open a sibling block',
    model=Arguments,
)
def run(arg: Arguments):
    from m.core.ci_tools import get_ci_tool
    tool = get_ci_tool()
    tool.close_block(arg.to_close)
    tool.open_block(arg.name, arg.description)
    return 0
