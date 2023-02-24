from m.cli import add_arg, command, run_main
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Prompt user for the next valid semantic version."""

    type: str = Field(
        proxy=add_arg(
            '--type',
            required=True,
            choices=['release', 'hotfix'],
            help='verification type',
        ),
    )
    version: str = Field(
        description='version to bump',
        positional=True,
        required=True,
    )


@command(
    name='bump_version',
    help='prompt for the next version',
    model=Arguments,
)
def run(arg: Arguments):
    from m.core.io import prompt_next_version

    return run_main(
        lambda: prompt_next_version(arg.version, arg.type),
        result_handler=print,
    )
