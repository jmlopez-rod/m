from m.cli import Arg, BaseModel, command, run_main


class Arguments(BaseModel):
    """Update the config and changelog files."""

    changelog: str = Arg(
        default='CHANGELOG.md',
        help='CHANGELOG filename',
    )
    m_dir: str = Arg(
        help='m project directory',
        positional=True,
        required=True,
    )
    new_ver: str = Arg(
        help='the new version',
        positional=True,
        required=True,
    )


@command(
    help='modify the config and changelog files',
    model=Arguments,
)
def run(arg: Arguments) -> int:
    from m.ci.release_setup import release_setup
    return run_main(
        lambda: release_setup(
            arg.m_dir,
            None,
            arg.new_ver,
            arg.changelog,
        ),
    )
