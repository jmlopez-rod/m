from m.cli import BaseModel, command


class Arguments(BaseModel):
    """Command line prompter.

    The goal is to display useful git information in the shell prompt.
    """


@command(
    help='print out a shell prompt with git info',
    model=Arguments,
)
def run() -> int:
    import sys

    from m.devcontainer.prompter import prompter

    sys.stdout.write(prompter())
    return 0
