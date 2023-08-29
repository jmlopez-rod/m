from m.cli import Arg, BaseModel, command, run_main
from m.cli.handlers import create_json_handler, create_yaml_handler
from m.core.io import env


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

    Or use the `--pretty` option to avoid piping.
    """

    owner: str = Arg(
        default=env('GITHUB_REPOSITORY_OWNER'),
        help='repo owner',
    )
    repo: str = Arg(
        help='repo name',
        required=True,
    )
    files: int = Arg(
        default=10,
        help='max number of files to retrieve',
    )
    pretty: bool = Arg(
        default=False,
        help='format json payload with indentation',
    )
    yaml: bool = Arg(
        default=False,
        help='use yaml format',
    )
    pr_number: int = Arg(
        help='the pr number',
        positional=True,
        required=True,
    )


@command(
    help='get information on a pull request',
    model=Arguments,
)
def run(arg: Arguments, arg_ns) -> int:
    from m.github.cli import get_pr_info
    result_handler = (
        create_yaml_handler(arg.pretty)
        if arg.yaml
        else create_json_handler(arg.pretty)
    )
    return run_main(
        lambda: get_pr_info(
            arg_ns.token,
            arg.owner,
            arg.repo,
            arg.pr_number,
            arg.files,
        ),
        result_handler=result_handler,
    )
