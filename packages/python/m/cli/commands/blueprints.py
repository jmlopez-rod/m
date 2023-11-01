from m.cli import Arg, BaseModel, command, env_var_or_empty, run_main


class Arguments(BaseModel):
    """Create the `[m_dir]/.m/blueprints` directory.

    This will add shell scripts to build the specified docker images as
    stated in the `[m_dir]/m.yaml` file.
    """

    m_dir: str = Arg(
        default='m',
        help='m project directory',
        positional=True,
    )
    m_tag: str = Arg(
        default='M_TAG',
        validator=env_var_or_empty,
        help='unique version to use for all the images',
    )
    cache_from_pr: str = Arg(
        default='M_CACHE_FROM_PR',
        validator=env_var_or_empty,
        help='pull request number to attempt to use as cache',
    )
    skip_makefile: bool = Arg(
        default=False,
        help='do not update Makefile',
    )
    skip_workflow: bool = Arg(
        default=False,
        help='do not update github workflow',
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
            m_tag=arg.m_tag,
            cache_from_pr=arg.cache_from_pr,
            update_makefile=not arg.skip_makefile,
            update_workflow=not arg.skip_workflow,
        ),
        result_handler=lambda _: None,
    )
