from m.cli import Arg, RemainderArgs, command, run_main
from pydantic import BaseModel


class Arguments(BaseModel):
    """Run pnpm in the devcontainer.

    This command is meant to be used as an alias for `pnpm` in a devcontainer.
    If you want view the help for the `pnpm` command you can run::

        command pnpm --help

    Depending on the pnpm command that we want to run, this command will change
    the working directory to the mounted volume and execute the pnpm command.

    Currently the main commands that will be executed in the mounted volume
    are

    - add
    - install
    - remove
    - uninstall

    If you need to run other commands in the mounted volume you can use the
    `--force-cd` flag.
    """

    force_cd: bool = Arg(default=False, help='force `cd` to the mounted volume')

    pnpm_args: list[str] = RemainderArgs(help='arguments to pass to pnpm')


@command(
    help='run pnpm in a devcontainer',
    model=Arguments,
)
def run(arg: Arguments):
    from m.devcontainer.pnpm import run_pnpm

    return run_main(
        lambda: run_pnpm(arg.pnpm_args, force_cd=arg.force_cd),
        result_handler=lambda _: None,
    )
