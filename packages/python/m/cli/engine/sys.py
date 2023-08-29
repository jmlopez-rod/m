import argparse as ap
from glob import iglob
from importlib import import_module
from os import path as pth
from typing import Callable, cast

from ..args import Meta
from .types import (
    CliCommands,
    CliSubcommands,
    CommandModule,
    CommandModuleMap,
    DecoratedRunFunction,
    MetaModule,
)

# Used as a default meta for the root command.
default_root_meta = MetaModule(
    meta=Meta(
        help='execute commands',
        description="""
            See the help for each of the following supported commands.
        """,
    ),
)


# Used as default meta for all Subcommands.
default_meta = MetaModule(
    meta=Meta(
        help='WIP - help message not set',
        description='WIP - description not set',
    ),
)


def _get_command_module(name: str) -> CommandModule | None:
    cmd_mod = import_module(name).__dict__
    run_func = cmd_mod.get('run')
    if run_func:
        return CommandModule(run=run_func)
    return None


def _get_meta_module(name: str, default: MetaModule) -> MetaModule:
    meta_mod = import_module(name).__dict__
    return MetaModule(
        meta=meta_mod.get('meta', default.meta),
        add_arguments=meta_mod.get('add_arguments', default.add_arguments),
    )


def get_command_modules(commands_module: str) -> dict[str, CommandModule]:
    """Create a dictionary of a file name to its module.

    These modules should define a `run` function.

    Args:
        commands_module: The full module resolution. For instance
            `m.cli.commands`.

    Returns:
        A dictionary of command modules.
    """
    cmd_module = import_module(commands_module)
    dir_name = pth.split(cmd_module.__file__ or '')[0]
    mod_names = list(iglob(f'{dir_name}/*.py'))
    mod = {}
    for mod_name in mod_names:
        name = pth.split(mod_name)[1][:-3]
        cmd_mod = _get_command_module(f'{commands_module}.{name}')
        if cmd_mod:
            mod[name] = cmd_mod
    return mod


def import_cli_commands(commands_module: str) -> CliCommands:
    """Gather the commands and subcommands for the cli.

    Args:
        commands_module: module containing all the commands.

    Returns:
        An instance of CliCommands gathered from the commands_module.
    """
    cmd_module = import_module(commands_module)
    if hasattr(cmd_module, 'create_cli_commands'):
        # No extra checks for now, if a module has this we assume that
        # it has the right signature.
        return cast(CliCommands, cmd_module.create_cli_commands())

    commands: dict[str, CommandModule | CliSubcommands] = {}
    root_cmd = get_command_modules(commands_module)

    for key, cmd_mod in root_cmd.items():
        commands[key] = cmd_mod

    root = pth.split(cmd_module.__file__ or '')[0]
    for cmd_name in iglob(f'{root}/*'):
        if cmd_name.endswith('.py') or cmd_name.endswith('__'):
            continue
        name = pth.split(cmd_name)[1]
        commands[name] = CliSubcommands(
            meta=_get_meta_module(f'{commands_module}.{name}', default_meta),
            subcommands=get_command_modules(f'{commands_module}.{name}'),
        )

    return CliCommands(
        meta=_get_meta_module(commands_module, default_root_meta),
        commands=commands,
    )


def subcommands(
    meta: MetaModule | None = None,
    **commands: DecoratedRunFunction,
) -> CliSubcommands:
    """Create a CliSubcommands instance.

    Args:
        meta: The meta for the command group.
        commands: The commands the group.

    Returns:
        An instance of CliSubcommands.
    """
    return CliSubcommands(
        meta=meta,
        subcommands={
            cmd_name: CommandModule(run=cmd_item)
            for cmd_name, cmd_item in commands.items()
        },
    )


def cli_commands(
    root_meta: MetaModule | None = None,
    **commands: DecoratedRunFunction | CliSubcommands,
) -> CliCommands:
    """Create a CliCommands instance.

    Args:
        root_meta: The meta for the root command.
        commands: The commands and subcommands for the cli.

    Returns:
        An instance of CliCommands.
    """
    root_meta = root_meta or default_root_meta
    return CliCommands(
        meta=root_meta,
        commands={
            cmd_name: (
                cmd_item
                if isinstance(cmd_item, CliSubcommands)
                else CommandModule(run=cmd_item)
            )
            for cmd_name, cmd_item in commands.items()
        },
    )


def command_group(
    *,
    help: str,   # noqa: WPS125
    description: str,
    add_arguments: Callable[[ap.ArgumentParser], None] | None = None,
) -> MetaModule:
    """Create an instance of a MetaModule.

    Named `cmd_group` since it is used to describe the group of commands.

    Args:
        help: quick help describing the module.
        description: Detailed description about the module.
        add_arguments: Optional function to handle the argparse instance.

    Returns:
        An instance of a MetaModule.
    """
    return MetaModule(
        meta=Meta(help=help, description=description),
        add_arguments=add_arguments,
    )


# A function to resolve merge conflicts between two Subcommands.
SubCmdResolution = Callable[[CommandModuleMap, CommandModuleMap], CommandModuleMap]


def merge_cli_commands(
    base: CliCommands,
    overrides: CliCommands,
    **resolutions: SubCmdResolution,
) -> CliCommands:
    """Merge two CliCommands instances.

    Resolutions may be provided to resolve merge conflicts between two
    subcommands.

    Args:
        base: The base CliCommands instance.
        overrides: The overrides CliCommands instance.
        resolutions: A dictionary of resolutions for subcommands.

    Returns:
        A new CliCommands instance.
    """
    commands: dict[str, CommandModule | CliSubcommands] = {**base.commands}
    for cmd_name, cmd_item in overrides.commands.items():
        resolution = resolutions.get(cmd_name)
        commands[cmd_name] = _get_new_command(cmd_name, commands, cmd_item, resolution)

    return CliCommands(
        meta=base.meta or overrides.meta,
        commands=commands,
    )


def _get_new_command(
    name: str,
    commands: dict[str, CommandModule | CliSubcommands],
    new_command_item: CliSubcommands | CommandModule,
    resolution: SubCmdResolution | None = None,
) -> CliSubcommands | CommandModule:
    if name in commands:
        if isinstance(new_command_item, CliSubcommands):
            current_command_item = commands.get(name)
            if isinstance(current_command_item, CliSubcommands):
                return CliSubcommands(
                    meta=new_command_item.meta or current_command_item.meta,
                    subcommands=_merge_subcommands(
                        current_command_item,
                        new_command_item,
                        resolution,
                    ),
                )
    return new_command_item


def _merge_subcommands(
    current_command_item: CliSubcommands,
    new_command_item: CliSubcommands,
    resolution: SubCmdResolution | None = None,
) -> CommandModuleMap:
    if resolution:
        return resolution(
            current_command_item.subcommands,
            new_command_item.subcommands,
        )
    return {
        **current_command_item.subcommands,
        **new_command_item.subcommands,
    }
