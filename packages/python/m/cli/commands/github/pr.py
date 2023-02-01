from m.cli import command, run_main
from pydantic import BaseModel, Field

from ...utils import env


class Arguments(BaseModel):
    """Retrieve a pull request information.

    example::

        $ m github pr --owner microsoft --repo typescript 44710 | m json
        {
            "headRefName": "ReduceExceptions",
            "headRefOid": "d9ae52cf49732a2d45b6cb7f4069205c88af39eb",
            "baseRefName": "main",
            "baseRefOid": "6452cfbad0afcc6d09b75e0a1e32da1d07e0b7ca",
            "title": "Reduce exceptions",
            "body": "...
    """

    owner: str = Field(
        default=env('GITHUB_REPOSITORY_OWNER'),
        description='repo owner',
    )
    repo: str = Field(
        description='repo name',
        required=True,
    )
    files: int = Field(
        default=10,
        description='max number of files to retrieve',
    )
    pr_number: int = Field(
        description='the pr number',
        positional=True,
        required=True,
    )


@command(
    name='pr',
    help='get information on a pull request',
    model=Arguments,
)
def run(arg: Arguments, arg_ns) -> int:
    from m.github.cli import get_pr_info
    return run_main(lambda: get_pr_info(
        arg_ns.token,
        arg.owner,
        arg.repo,
        arg.pr_number,
        arg.files,
    ))
