from m.cli import ArgProxy, BaseModel, command, env_var, run_main


class Arguments(BaseModel):
    """Create Github pull request(s) to review the release."""

    github_token: str = ArgProxy(
        '--github-token',
        type=env_var,
        default='GITHUB_TOKEN',
        help='Github personal access token with repo scope',
    )


@command(
    help='create release pull requests',
    model=Arguments,
)
def run(arg: Arguments):
    from m.ci.review_release import review_release

    return run_main(lambda: review_release(arg.github_token))
