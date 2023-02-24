from m.cli import add_arg, command, run_main
from m.core.io import env
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Start the release process.

    Depending on the workflow the `m` configuration is using we
    will be required to be working on the `master` or `develop` branch.

    It may also require input from the developer to proceed with
    certain operations.
    """

    github_token: str = Field(
        proxy=add_arg(
            '--github-token',
            default=env('GITHUB_TOKEN'),
            help='Github PAT (default: env.GITHUB_TOKEN)',
        ),
    )


@command(
    name='start_release',
    help='start the release process',
    model=Arguments,
)
def run(arg: Arguments):
    from m.ci.start_release import start_release

    return run_main(lambda: start_release(arg.github_token, hotfix=False))
