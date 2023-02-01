from m.cli import command, run_main
from pydantic import BaseModel


class Arguments(BaseModel):
    """Display the current git branch name.

    example::

        $ m git branch
        master
    """


@command(
    name='branch',
    help='display the current git branch',
    model=Arguments,
)
def run():
    from m import git
    return run_main(git.get_branch, print)
