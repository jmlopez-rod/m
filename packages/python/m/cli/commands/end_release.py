from m.cli import add_arg, command, run_main
from m.core.io import env
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """End the release process.

    Merges the release/hotfix branch into the master branch.
    """

    github_token: str = Field(
        proxy=add_arg(
            '--github-token',
            default=env('GITHUB_TOKEN'),
            help='Github PAT (default: env.GITHUB_TOKEN)',
        ),
    )


@command(
    name='end_release',
    help='end the release process',
    model=Arguments,
)
def run(arg: Arguments):
    from m.ci.end_release import end_release

    return run_main(lambda: end_release(arg.github_token))
