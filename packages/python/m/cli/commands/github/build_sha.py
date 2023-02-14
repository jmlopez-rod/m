from m.cli import command, run_main
from m.core.io import env
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    r"""Provide the build sha.

    Given the GITHUB_SHA (a merge commit it fetches the sha of the actual
    commit we thought we were building.

    example::

        $ m github build_sha \
            --owner jmlopez-rod \
            --repo m \
            --sha 6bf3a8095891c551043877b922050d5b01d20284
        fa6a600729ffbe1dfd7fece76ef4566e45fbfe40

    The sha can be obtained in Github by looking at the output of the
    checkout action.

    The `owner` option defaults to the value of the environment variable
    `GITHUB_REPOSITORY_OWNER`.
    """

    owner: str = Field(
        default=env('GITHUB_REPOSITORY_OWNER'),
        description='repo owner',
    )
    repo: str = Field(
        description='repo name',
        required=True,
    )
    sha: str = Field(
        description='commit sha',
        required=True,
    )


@command(
    name='build_sha',
    help='get the correct commit sha',
    model=Arguments,
)
def run(arg: Arguments, arg_ns) -> int:
    from m.github.ci import get_build_sha
    return run_main(
        lambda: get_build_sha(arg_ns.token, arg.owner, arg.repo, arg.sha),
        result_handler=print,
    )
