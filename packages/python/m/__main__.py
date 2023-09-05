from m.cli import exec_cli, import_cli_commands
from m.log import logging_config


def main():
    """Execute the cli."""
    logging_config()
    cli_commands = import_cli_commands('m.cli.commands')
    exec_cli(cli_commands)


if __name__ == '__main__':  # pragma: no cover
    main()
