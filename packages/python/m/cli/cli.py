import argparse
import sys
from os import path as pth
from typing import Any, Callable, cast
from warnings import warn

import argcomplete
from m.core import Bad, Issue, OneOf
from m.log import Logger

from ..core.io import env
from .engine.misc import params_count
from .engine.sys import (
    default_meta,
    default_root_meta,
    get_cli_command_modules,
    merge_cli_commands,
)
from .engine.types import CliCommands, CliSubcommands, CommandModule
from .handlers import create_issue_handler, create_json_handler
from .validators import validate_non_empty_str

logger = Logger('m.cli')
cli_global_option = Callable[[argparse.ArgumentParser], argparse.Action]


default_result_handler = create_json_handler(pretty=False)
default_issue_handler = create_issue_handler(use_warning=False)


def _main_parser(
    cli_commands: CliCommands,
    add_args: Callable[[argparse.ArgumentParser], None] | None = None,
) -> argparse.Namespace:
    root_meta = (cli_commands.meta or default_root_meta).meta
    raw = argparse.RawTextHelpFormatter
    # NOTE: In the future we will need to extend from this class to be able to
    #   override the error method to be able to print CI environment messages.
    argp = argparse.ArgumentParser(
        formatter_class=raw,
        description=root_meta['description'] if root_meta else '...',
    )
    if add_args:
        add_args(argp)
    subp = argp.add_subparsers(
        title='commands',
        dest='command_name',
        required=True,
        help='additional help',
        metavar='<command>',
    )
    names = sorted(cli_commands.commands.keys())
    for name in names:
        cmd_item = cli_commands.commands[name]
        if isinstance(cmd_item, CliSubcommands):
            subcmd_mod = cmd_item
            meta_mod = subcmd_mod.meta or default_meta
            meta_dict = meta_mod.meta
            parser = subp.add_parser(
                name,
                help=meta_dict['help'],
                formatter_class=raw,
                description=meta_dict['description'],
            )
            if meta_mod.add_arguments:
                meta_mod.add_arguments(parser)
            subsubp = parser.add_subparsers(
                title='commands',
                dest='subcommand_name',
                required=True,
                help='additional help',
                metavar='<command>',
            )
            sub_mod = subcmd_mod.subcommands
            for subname in sorted(sub_mod.keys()):
                run_func = sub_mod[subname].run
                if params_count(run_func) == 3:
                    run_func(subname, None, subsubp)
        else:
            mod_inst = cmd_item
            run_func = mod_inst.run
            if params_count(run_func) == 3:
                run_func(name, None, subp)
    argcomplete.autocomplete(argp)
    return argp.parse_args()


def run_cli(
    commands_module: str | None,
    add_args: Callable[[argparse.ArgumentParser], None] | None = None,
    extra_commands: CliCommands | None = None,
) -> None:
    """Run the cli application.

    usage::

        def add_args(argp):
            argp.add_argument(...)
        def main():
            run_cli('m.cli.commands', add_args)

    We only need `add_args` if we need to gain access to the
    `argparse.ArgumentParser` instance.

    Args:
        commands_module: The full name of the module containing the commands.
        add_args: Optional callback to gain access to the ArgumentParser.
        extra_commands: A tuple containing command modules and meta modules.
    """
    # NOTE: This is a deprecated feature and will be removed in the future.
    if commands_module and '/' in commands_module:  # pragma: no cover
        warn(
            '`run_cli(__file__)` is deprecated, use `run_cli("commands.module") instead',
            DeprecationWarning,
        )
        root = pth.split(pth.split(commands_module)[0])[1]
        commands_module = f'{root}.cli.commands'
    cli_commands: CliCommands = CliCommands(commands={}, meta=default_root_meta)
    if commands_module:
        cli_commands = get_cli_command_modules(commands_module)
    if extra_commands:
        cli_commands = merge_cli_commands(cli_commands, extra_commands)
    arg = _main_parser(cli_commands, add_args)

    run_func = None
    command_name = ''

    commands = cli_commands.commands
    if hasattr(arg, 'subcommand_name'):
        command_name = arg.subcommand_name
        sub_mod = cast(CliSubcommands, commands[arg.command_name])
        run_func = sub_mod.subcommands[command_name].run

    else:
        command_name = arg.command_name
        run_func = cast(CommandModule, commands[command_name]).run

    len_run_args = params_count(run_func)
    run_args = [command_name, arg, None][:len_run_args]
    exit_code = 0
    try:
        # mypy is having a hard time figuring out the type of run_args
        exit_code = run_func(*run_args)  # type:ignore[arg-type]
    except Exception as ex:
        default_issue_handler(
            Issue('unknown cli run function exception', cause=ex),
        )
        exit_code = 5
    sys.exit(exit_code)


def run_main(
    callback: Callable[[], OneOf[Issue, Any]],
    result_handler: Callable[[Any], None] = default_result_handler,
    issue_handler: Callable[[Issue], None] = default_issue_handler,
) -> int:
    """Run the callback and print the returned value.

    To change how the result or an issue should be display provide the optional
    arguments `handle_result` and `handle_issue`. For instance, to display the
    raw value provide the `print` function.

    Args:
        callback: A function that returns a `OneOf`.
        result_handler: A function that takes in the Good result.
        issue_handler: A function that takes in the Issue.

    Returns:
        0 if the callback is a `Good` result otherwise return 1.
    """
    res = None
    try:
        res = callback()
    except Exception as ex:
        issue_handler(Issue('unknown caught exception', cause=ex))
        return 2
    if isinstance(res, Bad):
        problem = res.value
        if isinstance(problem, Issue):
            issue_handler(problem)
        else:
            issue_handler(Issue('non-issue exception', cause=problem))
        return 1
    result_handler(res.value)
    return 0


def cli_integration_token(
    integration: str,
    env_var: str,
) -> cli_global_option:
    """Return a function that takes in a parser.

    This generated function registers a token argument in the parser
    which looks for its value in the environment variables.

    Args:
        integration: The name of the integration.
        env_var: The environment variable name.

    Returns:
        A function to add arguments to an argparse parser.
    """
    return lambda parser: parser.add_argument(
        '-t',
        '--token',
        type=validate_non_empty_str,
        default=env(env_var),
        help=f'{integration} access token (default: env.{env_var})',
    )
