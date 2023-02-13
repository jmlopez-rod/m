from m.cli import command, run_main
from m.core.io import env
from pydantic import BaseModel, Field


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

    owner: str = Field(
        default=env('GITHUB_REPOSITORY_OWNER'),
        description='repo owner',
    )
    repo: str = Field(
        description='repo name',
        required=True,
    )
    commit_title: str | None = Field(
        description='commit title',
    )
    pr: int = Field(
        description='the pr number',
        positional=True,
        required=True,
    )


@command(
    name='merge_pr',
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
