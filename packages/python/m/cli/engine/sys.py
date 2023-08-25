from glob import iglob
from importlib import import_module
from os import path as pth
from typing import Tuple

from .types import CmdMap, CommandModule, MetaMap, MetaModule, NestedCmdMap


def _get_command_module(name: str) -> CommandModule | None:
    cmd_mod = import_module(name).__dict__
    run_func = cmd_mod.get('run')
    if run_func:
        return CommandModule(run=run_func)
    return None


def _get_meta_module(name: str) -> MetaModule:
    meta_mod = import_module(name).__dict__
    return MetaModule(
        meta=meta_mod['meta'],
        add_arguments=meta_mod.get('add_arguments'),
    )


def get_command_modules(commands_module: str) -> CmdMap:
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


def get_cli_command_modules(commands_module: str) -> Tuple[NestedCmdMap, MetaMap]:
    """Return a dictionary containing the commands and subcommands for the cli.

    Args:
        commands_module: module containing all the commands.

    Returns:
        A tuple with a map containing all the modules that have the commands
        for the cli and a map with the meta data related to each command.
    """
    cmd_module = import_module(commands_module)
    root_cmd = get_command_modules(commands_module)
    mod: NestedCmdMap = {}
    meta: MetaMap = {}
    for key, cmd_mod in root_cmd.items():
        mod[key] = cmd_mod
    meta['_root'] = _get_meta_module(commands_module)
    root = pth.split(cmd_module.__file__ or '')[0]
    subcommands = list(iglob(f'{root}/*'))
    for cmd_name in subcommands:
        if cmd_name.endswith('.py') or cmd_name.endswith('__'):
            continue
        name = pth.split(cmd_name)[1]
        mod[name] = get_command_modules(f'{commands_module}.{name}')
        meta[name] = _get_meta_module(f'{commands_module}.{name}')
    return mod, meta
