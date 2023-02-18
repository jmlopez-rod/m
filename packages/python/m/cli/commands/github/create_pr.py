from m.cli import command, run_main, validate_payload
from m.core.io import env
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    r"""Create a pull request.

    https://docs.github.com/en/rest/reference/pulls#create-a-pull-request

    example::

        $ m github create_pr \
            --owner jmlopez-rod \
            --repo repo \
            --head feature_branch \
            --base master \
            --title 'PR Title' \
            @file_with_pr_body | m json
    """

    owner: str = Field(
        default=env('GITHUB_REPOSITORY_OWNER'),
        description='repo owner',
    )
    repo: str = Field(
        description='repo name',
        required=True,
    )
    head: str = Field(
        description='name of the branch where the changes are implemented',
        required=True,
    )
    base: str = Field(
        description='name of the branch you want the changes pulled into',
        required=True,
    )
    title: str = Field(
        description='pull request title',
        required=True,
    )
    body: str = Field(
        default='@-',
        description='data: @- (stdin), @filename (file), string',
        validator=validate_payload,
        positional=True,
    )


@command(
    name='create_pr',
    help='create a pull request',
    model=Arguments,
)
def run(arg: Arguments, arg_ns) -> int:
    from m.github.api import GithubPullRequest, create_pr
    return run_main(lambda: create_pr(
        arg_ns.token,
        arg.owner,
        arg.repo,
        GithubPullRequest(
            title=arg.title,
            body=arg.body,
            head=arg.head,
            base=arg.base,
        ),
    ))
