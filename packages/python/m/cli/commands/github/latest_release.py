from m.cli import Arg, BaseModel, command, run_main
from m.core.io import env


class Arguments(BaseModel):
    """Retrieve the latest release.

    example::

        $ m github latest_release --owner microsoft --repo typescript
    """

    owner: str = Arg(
        default=env('GITHUB_REPOSITORY_OWNER'),
        help='repo owner',
    )
    repo: str = Arg(
        help='repo name',
        required=True,
    )


@command(
    help='get the latest release for a repo',
    model=Arguments,
)
def run(arg: Arguments, arg_ns) -> int:
    from m.github.cli import get_latest_release
    return run_main(
        lambda: get_latest_release(
            arg_ns.token,
            arg.owner,
            arg.repo,
        ), print,
    )
