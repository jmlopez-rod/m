from m.cli import command, run_main
from m.core.io import env
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Start the release process for a hotfix.

    A hotfix should always be done in the master branch.

    It may also require input from the developer to proceed with
    certain operations.
    """

    github_token: str = Field(
        default=env('GITHUB_TOKEN'),
        description='github PAT',
    )


@command(
    name='start_hotfix',
    help='start the release process for a hotfix',
    model=Arguments,
)
def run(arg: Arguments):
    from m.ci.start_release import start_release

    return run_main(lambda: start_release(arg.github_token, hotfix=True))
