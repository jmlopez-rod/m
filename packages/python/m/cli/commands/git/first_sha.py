from m.cli import BaseModel, command, run_main


class Arguments(BaseModel):
    """Display the very first commit sha in the repository.

    example::

        $ m git first_sha
        bf286e270e13c75dfed289a3921289092477c058
    """


@command(
    help='display the first commit sha',
    model=Arguments,
)
def run():
    from m import git
    return run_main(git.get_first_commit_sha, print)
