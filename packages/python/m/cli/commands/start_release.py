from m.cli import command, run_main
from pydantic import BaseModel


class Arguments(BaseModel):
    """Start the release process.

    Depending on the workflow the `m` configuration is using we
    will be required to be working on the `master` or `develop` branch.

    It may also require input from the developer to proceed with
    certain operations.
    """


@command(
    name='start_release',
    help='start the release process',
    model=Arguments,
)
def run():
    from m.ci.start_release import start_release

    return run_main(start_release)
