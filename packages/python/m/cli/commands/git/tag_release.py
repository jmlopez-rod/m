from m.cli import Arg, BaseModel, command, run_main


class Arguments(BaseModel):
    """Supplement to `m github release`.

    This command needs the `git` cli and it is meant to be run after
    `m github release` to create a major and minor release tags.


    example::

        $ m git tag_release --version 1.2.3


    It will create or update the following tags::

        -v1
        -v1.2

    Note that the tags may be moved with each release to point to the latest
    release. This is done by deleting the tag and creating it again.
    """

    version: str = Arg(
        help='version to create tags from',
        required=True,
    )
    sha: str = Arg(
        default='',
        help='sha to tag',
    )
    major_only: bool = Arg(
        default=False,
        help='only create major tag',
    )


@command(
    help='tag github releases',
    model=Arguments,
)
def run(arg: Arguments) -> int:
    from m import git
    return run_main(
        lambda: git.tag_release(arg.version, arg.sha, major_only=arg.major_only),
        result_handler=print,
    )
