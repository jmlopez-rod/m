from m.cli import Arg, BaseModel, command, run_main


class Arguments(BaseModel):
    """Create the [m_dir]/.m/docker-images directory.

    This will add shell scripts to build the specified docker images as
    stated in the `[m_dir]/m.yaml` file.
    """

    m_dir: str = Arg(
        default='m',
        help='m project directory',
        positional=True,
    )


@command(
    help='create docker images blueprints',
    model=Arguments,
)
def run(arg: Arguments) -> int:
    from m.ci.m_blueprints import write_blueprints

    return run_main(
        lambda: write_blueprints(arg.m_dir),
        result_handler=lambda _: None,
    )
