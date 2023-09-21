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
    update_makefile: bool = Arg(
        default=False,
        help='update Makefile',
    )
    update_workflow: bool = Arg(
        default=False,
        help='update github workflow',
    )


@command(
    help='create docker images blueprints',
    model=Arguments,
)
def run(arg: Arguments) -> int:
    from m.ci.m_blueprints import write_blueprints

    return run_main(
        lambda: write_blueprints(
            arg.m_dir,
            update_makefile=arg.update_makefile,
            update_workflow=arg.update_workflow,
        ),
        result_handler=lambda _: None,
    )
