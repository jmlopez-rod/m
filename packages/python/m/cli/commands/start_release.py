from m.cli import ArgProxy, BaseModel, command, env_var, run_main


class Arguments(BaseModel):
    """Start the release process.

    Depending on the workflow the `m` configuration is using we
    will be required to be working on the `master` or `develop` branch.

    It may also require input from the developer to proceed with
    certain operations.
    """

    github_token: str = ArgProxy(
        '--github-token',
        default='GITHUB_TOKEN',
        type=env_var,
        help='Github personal access token with repo scope',
    )


@command(
    help='start the release process',
    model=Arguments,
)
def run(arg: Arguments):
    from m.ci.start_release import start_release

    return run_main(lambda: start_release(arg.github_token, hotfix=False))
