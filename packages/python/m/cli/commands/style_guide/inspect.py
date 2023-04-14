from m.cli import command, run_main
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Inspect the style guide.

    Inspects the style guide for errors.
    """

    style_file: str = Field(
        description='Name of the file containing the style guide.',
        positional=True,
    )


@command(
    name='inspect',
    help='inspect the style guide',
    model=Arguments,
)
def run(arg: Arguments):
    from m.style_guide.inspect import read_style_guide

    return run_main(lambda: read_style_guide(arg.style_file))
