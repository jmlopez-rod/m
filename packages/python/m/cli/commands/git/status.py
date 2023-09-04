from m.cli import Arg, BaseModel, command, run_main


class Arguments(BaseModel):
    """Display a single word representing the current git status.

    example::

        $ m git status
        clean

    statuses::

        unknown
        untracked
        clean
        ahead
        behind
        staged
        dirty
        diverged
        ?

    If you want to check for stashed changes, use the `--check-stashed` flag.
    """

    check_stashed: bool = Arg(
        default=False,
        help='check if there are any stashed changes',
    )


def _get_status(status_desc: tuple[str, str]) -> str:
    return status_desc[0]


@command(
    help='display the current git status',
    model=Arguments,
)
def run(arg: Arguments):
    from m import git

    return run_main(
        lambda: git.get_status(check_stash=arg.check_stashed).map(_get_status),
        print,
    )
