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


def get_command_modules(root: str, commands_module: str) -> CmdMap:
    """Create a dictionary of a file name to its module.

    These modules should define a `run` function.

    Args:
        root: Absolute path of the directory containing the __main__.py module
            that activates the cli.
        commands_module: The full module resolution. For instance
            `m.cli.commands`.

    Returns:
        A dictionary of command modules.
    """
    dir_name = '/'.join(commands_module.split('.')[1:])
    mod_names = list(iglob(f'{root}/{dir_name}/*.py'))
    mod = {}
    for mod_name in mod_names:
        name = pth.split(mod_name)[1][:-3]
        cmd_mod = _get_command_module(f'{commands_module}.{name}')
        if cmd_mod:
            mod[name] = cmd_mod
    return mod


def get_cli_command_modules(file_path: str) -> Tuple[NestedCmdMap, MetaMap]:
    """Return a dictionary containing the commands and subcommands for the cli.

    `file_path` is expected to be the absolute path to the __main__.py file.
    Another restriction is that the __main__.py file must have the
    `cli.commands` module as its sibling.

    Args:
        file_path: Absolute path to the `__main__.py` file.

    Returns:
        A tuple with a map containing all the modules that have the commands
        for the cli and a map with the meta data related to each command.
    """
    root = pth.split(pth.abspath(file_path))[0]
    main_mod = pth.split(root)[1]
    cli_root = f'{main_mod}.cli'
    root_cmd = get_command_modules(root, f'{cli_root}.commands')
    mod: NestedCmdMap = {}
    meta: MetaMap = {}
    for key, cmd_mod in root_cmd.items():
        mod[key] = cmd_mod
    meta['_root'] = _get_meta_module(f'{cli_root}.commands')
    subcommands = list(iglob(f'{root}/cli/commands/*'))
    for cmd_name in subcommands:
        if cmd_name.endswith('.py') or cmd_name.endswith('__'):
            continue
        name = pth.split(cmd_name)[1]
        mod[name] = get_command_modules(root, f'{cli_root}.commands.{name}')
        meta[name] = _get_meta_module(f'{cli_root}.commands.{name}')
    return mod, meta
