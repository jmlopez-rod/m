from m.cli import Arg, BaseModel, command, run_main


class Arguments(BaseModel):
    """Add tags to a package version.

        $ m npm add_tags --branch "$M_BRANCH" <package-name> <m_tag>

    These tags are the same tags generated from docker.
    """

    package_name: str = Arg(
        help='name of the npm package',
        positional=True,
        required=True,
    )

    m_tag: str = Arg(
        help='the m_tag of the published package',
        positional=True,
        required=True,
    )

    branch: str = Arg(
        help='the branch where the build is taking place',
        required=True,
    )


@command(
    help='add tags to an npm package version',
    model=Arguments,
)
def run(arg: Arguments):
    from m.npm.add_tags import add_tags
    return run_main(lambda: add_tags(arg.package_name, arg.m_tag, arg.branch))
