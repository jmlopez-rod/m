from m.cli import add_arg, command, run_main
from m.core.io import env
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Create Github pull request(s) to review the release."""

    github_token: str = Field(
        proxy=add_arg(
            '--github-token',
            default=env('GITHUB_TOKEN'),
            help='Github PAT (default: env.GITHUB_TOKEN)',
        ),
    )


@command(
    name='review_release',
    help='create release pull requests',
    model=Arguments,
)
def run(arg: Arguments):
    from m.ci.review_release import review_release

    return run_main(lambda: review_release(arg.github_token))
