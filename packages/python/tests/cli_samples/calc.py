import logging

from m.cli import (
    Arg,
    BaseModel,
    CliCommands,
    cli_commands,
    command,
    command_group,
    exec_cli,
    subcommands,
)
from m.log import logging_config


class HelloArg(BaseModel):
    """Say hello to someone."""

    name: str = Arg(help='your name', positional=True, required=True)

@command(
    help='say hello',
    model=HelloArg,
)
def say_hello(arg: HelloArg) -> int:
    """See description in HelloArg."""
    print(f'Hello {arg.name}')
    return 0


class BaseArgs(BaseModel):
    """Provides two arguments.

    Override in final command to update description.
    """

    x: int = Arg(help='first number', positional=True, required=True)
    y: int = Arg(help='second number', positional=True, required=True)

class AddArgs(BaseArgs):
    """Add two numbers."""


@command(
    help='add numbers',
    model=AddArgs,
)
def add_numbers(arg: AddArgs) -> int:
    """See description in AddArgs."""
    print(arg.x + arg.y)
    return 0


class MultiplyArgs(BaseArgs):
    """Multiply two numbers."""


@command(
    help='multiply numbers',
    model=MultiplyArgs,
)
def multiply_numbers(arg: MultiplyArgs) -> int:
    """See description in MultiplyArgs."""
    print(arg.x * arg.y)
    return 0


def create_cli_commands() -> CliCommands:
    """Create the cli commands."""
    return cli_commands(
        command_group(
            help='CLI ROOT - will not display',
            description="""Custom description for the cli."""
        ),
        say_hello=say_hello,
        calculator=subcommands(
            command_group(
                help='provides basic operations',
                description="""
                    This is a description for the calculator group.
                """,
            ),
            add=add_numbers,
            mul=multiply_numbers,
        ),
    )

def main():
    """Execute the cli."""
    logging_config(logging.NOTSET)
    cli_cmds = create_cli_commands()
    exec_cli(cli_cmds)


if __name__ == '__main__':
    main()
