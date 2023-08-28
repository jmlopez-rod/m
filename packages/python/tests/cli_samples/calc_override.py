import logging

from m.cli import (
    Arg,
    CliCommands,
    cli_commands,
    command,
    command_group,
    exec_cli,
    import_cli_commands,
    merge_cli_commands,
    subcommands,
)
from m.log import logging_config
from tests.cli_samples.calc import BaseArgs


class ThreeArgs(BaseArgs):
    """Provides three arguments."""

    z: int = Arg(help='third number', positional=True, required=True)


class AddArgs(ThreeArgs):
    """Add three numbers."""


@command(
    help='add 3 numbers',
    model=AddArgs,
)
def add_numbers(arg: AddArgs) -> int:
    """See description in AddArgs."""
    print(arg.x + arg.y + arg.z)
    return 0


def create_cli_commands() -> CliCommands:
    """Create the cli commands."""
    base_cli_cmds = import_cli_commands('tests.cli_samples.calc')
    overrides = cli_commands(
        calculator=subcommands(
            add3=add_numbers,
        ),
        mini=subcommands(
            command_group(
                help='calculator 3',
                description='no override',
            ),
            add=add_numbers,
        ),
        calc=subcommands(
            add3=add_numbers,
        ),
    )
    return merge_cli_commands(
        base_cli_cmds,
        overrides,
        calculator=lambda a, b: dict(
            add=a['add'],
            add3=b['add3'],
        ),
    )


def main():
    """Execute the cli."""
    logging_config(logging.NOTSET)
    cli_cmds = create_cli_commands()
    exec_cli(cli_cmds)


if __name__ == '__main__':
    main()
