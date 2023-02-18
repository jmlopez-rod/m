from m.cli import command, run_main
from m.core.io import env
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Retrieve the latest release.

    example::

        $ m github latest_release --owner microsoft --repo typescript
    """

    owner: str = Field(
        default=env('GITHUB_REPOSITORY_OWNER'),
        description='repo owner',
    )
    repo: str = Field(
        description='repo name',
        required=True,
    )


@command(
    name='latest_release',
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
