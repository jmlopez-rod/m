from m.cli import ArgProxy, BaseModel, command, env_var, run_main


class Arguments(BaseModel):
    """End the release process.

    Merges the release/hotfix branch into the master branch.
    """

    github_token: str = ArgProxy(
        '--github-token',
        default='GITHUB_TOKEN',
        type=env_var,
        help='Github personal access token with repo scope',
    )


@command(
    help='end the release process',
    model=Arguments,
)
def run(arg: Arguments):
    from m.ci.end_release import end_release

    return run_main(lambda: end_release(arg.github_token))
