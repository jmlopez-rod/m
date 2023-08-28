from m.cli import Arg, BaseModel, command, run_main
from m.core.io import env


class Arguments(BaseModel):
    r"""Create a release in Github.

    https://docs.github.com/en/rest/reference/repos#create-a-release

    example::

        $ m github release \
            --owner jmlopez-rod \
            --repo pysync \
            --version 1.0.0

    The `owner` option defaults to the value of the environment variable
    `GITHUB_REPOSITORY_OWNER`.
    """

    owner: str = Arg(
        default=env('GITHUB_REPOSITORY_OWNER'),
        help='repo owner',
    )
    repo: str = Arg(
        help='repo name',
        required=True,
    )
    version: str = Arg(
        help='version to release',
        required=True,
    )
    branch: str | None = Arg(
        help='The branch where the git tag will be created',
    )


@command(
    help='create a github release',
    model=Arguments,
)
def run(arg: Arguments, arg_ns) -> int:
    from m.github.api import create_release
    return run_main(
        lambda: create_release(
            arg_ns.token,
            arg.owner,
            arg.repo,
            arg.version,
            arg.branch,
        ),
    )
