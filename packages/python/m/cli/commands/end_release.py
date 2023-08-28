from m.cli import ArgProxy, BaseModel, command, run_main
from m.core.io import env


class Arguments(BaseModel):
    """End the release process.

    Merges the release/hotfix branch into the master branch.
    """

    github_token: str = ArgProxy(
        '--github-token',
        default=env('GITHUB_TOKEN'),
        help='Github PAT (default: env.GITHUB_TOKEN)',
    )


@command(
    help='end the release process',
    model=Arguments,
)
def run(arg: Arguments):
    from m.ci.end_release import end_release

    return run_main(lambda: end_release(arg.github_token))
