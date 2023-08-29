from m.cli import Arg, BaseModel, command, run_main
from m.core.io import env


class Arguments(BaseModel):
    r"""Merge a pull request.

    https://docs.github.com/en/rest/reference/pulls#merge-a-pull-request

    example::

        $ m github merge_pr \\
            --owner owner \\
            --repo repo \\
            --commit-title 'commit_title' \\
            99
    """

    owner: str = Arg(
        default=env('GITHUB_REPOSITORY_OWNER'),
        help='repo owner',
    )
    repo: str = Arg(
        help='repo name',
        required=True,
    )
    commit_title: str | None = Arg(
        help='commit title',
    )
    pr: int = Arg(
        help='the pr number',
        positional=True,
        required=True,
    )


@command(
    help='merge a pull request',
    model=Arguments,
)
def run(arg: Arguments, arg_ns) -> int:
    from m.github.api import merge_pr
    return run_main(lambda: merge_pr(
        arg_ns.token,
        arg.owner,
        arg.repo,
        arg.pr,
        arg.commit_title,
    ))
