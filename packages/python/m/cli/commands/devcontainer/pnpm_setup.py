from m.cli import Arg, command, run_main
from pydantic import BaseModel


class Arguments(BaseModel):
    """Setup pnpm in the devcontainer.

    This command is meant run from inside the devcontainer. It will
    create several symbolic links so that the pnpm data may be stored in a
    volume and thus be able to be shared with other devcontainers.
    """

    work_dir: str = Arg(
        help='the work directory containing package.json',
        positional=True,
        required=True,
    )

    pnpm_dir: str = Arg(
        help='the directory where pnpm data will be stored',
        positional=True,
        required=True,
    )


@command(
    help='setup pnpm',
    model=Arguments,
)
def run(arg: Arguments):
    from m.devcontainer.pnpm import pnpm_setup

    return run_main(
        lambda: pnpm_setup(arg.work_dir, arg.pnpm_dir),
    )
