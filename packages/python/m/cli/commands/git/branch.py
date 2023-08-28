from m.cli import BaseModel, command, run_main


class Arguments(BaseModel):
    """Display the current git branch name.

    example::

        $ m git branch
        master
    """


@command(
    help='display the current git branch',
    model=Arguments,
)
def run():
    from m import git
    return run_main(git.get_branch, print)
