from m.cli import Arg, ArgProxy, BaseModel, command, run_main


class Arguments(BaseModel):
    """Prompt user for the next valid semantic version."""

    type: str = ArgProxy(
        '--type',
        required=True,
        choices=['release', 'hotfix'],
        help='verification type',
    )
    version: str = Arg(
        help='version to bump',
        positional=True,
        required=True,
    )


@command(
    help='prompt for the next version',
    model=Arguments,
)
def run(arg: Arguments):
    from m.core.io import prompt_next_version

    return run_main(
        lambda: prompt_next_version(arg.version, arg.type),
        result_handler=print,
    )
