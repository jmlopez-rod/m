from m.cli import BaseModel, command, run_main


class Arguments(BaseModel):
    """Display a single word representing the current git status.

    example::

        $ m git status
        clean

    statuses::

        unknown
        untracked
        stash
        clean
        ahead
        behind
        staged
        dirty
        diverged
        ?
    """


def _get_status(status_desc: tuple[str, str]) -> str:
    return status_desc[0]


@command(
    name='status',
    help='display the current git status',
    model=Arguments,
)
def run():
    from m import git
    return run_main(
        lambda: git.get_status().map(_get_status),
        print,
    )
