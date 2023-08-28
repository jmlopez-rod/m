from m.cli import Arg, BaseModel, command, run_main
from m.cli.handlers import create_dict_handler
from m.core.io import env


class Arguments(BaseModel):
    """Retrieve pull requests associated with a branch.

    example::

        $ m github branch_prs --owner jmlopez-rod --repo m release/0.18.0
    """

    pretty: bool = Arg(
        default=False,
        help='format json payload with indentation',
    )
    yaml: bool = Arg(
        default=False,
        help='use yaml format',
    )
    owner: str = Arg(
        default=env('GITHUB_REPOSITORY_OWNER'),
        help='repo owner',
    )
    repo: str = Arg(
        help='repo name',
        required=True,
    )
    branch: str = Arg(
        help='branch name',
        required=True,
        positional=True,
    )


@command(
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
