from m.cli import BaseModel, command


class Arguments(BaseModel):
    """Command line prompter.

    The goal is to display useful git information in the prompt.
    """


@command(
    help='print out a bash snippet that exports variables',
    model=Arguments,
)
def run() -> int:
    import sys

    from m.devcontainer.prompter import prompter

    sys.stdout.write(prompter())
    return 0
