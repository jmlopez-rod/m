from m.cli import Arg, ArgProxy, BaseModel, command, run_main
from m.core.io import env


class Arguments(BaseModel):
    r"""Create a commit status.

    - https://docs.github.com/en/rest/reference/repos#create-a-commit-status

    example::

        $ m github status \
            --owner jmlopez-rod \
            --repo pysync \
            --sha [sha] \
            --context github-check \
            --state pending \
            --description 'running checks'

    The `owner` option defaults to the value of the environment variable
    `GITHUB_REPOSITORY_OWNER`.
    """

    owner: str = Arg(
        default=env('GITHUB_REPOSITORY_OWNER'),
        help='repo owner',
    )
    repo: str = Arg(
        help='repo name',
        required=True,
    )
    sha: str = Arg(
        help='commit sha',
        required=True,
    )
    context: str = Arg(
        help='unique identifier for the status (a name?)',
        required=True,
    )
    state: str = ArgProxy(
        '--state',
        required=True,
        choices=['error', 'failure', 'pending', 'success'],
        help='the state of the status',
    )
    description: str = Arg(
        help='a short description of the status',
        required=True,
    )
    url: str | None = Arg(
        help='URL to associate with this status',
    )


@command(
    help='create a commit status',
    model=Arguments,
)
def run(arg: Arguments, arg_ns) -> int:
    from m.github.api import GithubShaStatus, commit_status
    return run_main(
        lambda: commit_status(
            arg_ns.token,
            arg.owner,
            arg.repo,
            GithubShaStatus(
                sha=arg.sha,
                context=arg.context,
                state=arg.state,
                description=arg.description,
                url=arg.url,
            ),
        ),
    )
