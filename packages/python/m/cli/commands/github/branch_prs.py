from m.cli import command, run_main
from m.cli.handlers import create_dict_handler
from m.core.io import env
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Retrieve pull requests associated with a branch.

    example::

        $ m github branch_prs --owner jmlopez-rod --repo m release/0.18.0
    """

    pretty: bool = Field(
        default=False,
        description='format json payload with indentation',
    )
    yaml: bool = Field(
        default=False,
        description='use yaml format',
    )
    owner: str = Field(
        default=env('GITHUB_REPOSITORY_OWNER'),
        description='repo owner',
    )
    repo: str = Field(
        description='repo name',
        required=True,
    )
    branch: str = Field(
        description='branch name',
        required=True,
        positional=True,
    )


@command(
    name='branch_prs',
    help='get prs associated with a branch',
    model=Arguments,
)
def run(arg: Arguments, arg_ns) -> int:
    from m.github.graphql.queries.branch_prs import fetch_raw

    return run_main(
        lambda: fetch_raw(
            arg_ns.token,
            arg.owner,
            arg.repo,
            arg.branch,
        ),
        result_handler=create_dict_handler(arg.pretty, as_yaml=arg.yaml),
    )
