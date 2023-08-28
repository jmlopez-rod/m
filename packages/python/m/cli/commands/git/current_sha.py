from m.cli import BaseModel, command, run_main


class Arguments(BaseModel):
    """Display the current commit sha.

    example::

        $ m git current_sha
        74075a3ea5c9252a0f2b9fd6b095567b3b9b4028
    """


@command(
    help='display the current commit sha',
    model=Arguments,
)
def run():
    from m import git
    return run_main(git.get_current_commit_sha, print)
