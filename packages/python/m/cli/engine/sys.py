from glob import iglob
from importlib import import_module
from os import path as pth
from typing import cast

from .types import CmdMap, CmdModule, NestedCmdMap


def import_mod(name: str) -> CmdModule:
    """Import a module by string.

    Args:
        name: The full module name, i.e path.to.module

    Returns:
        A module that we hope has the shape of CmdModule.
    """
    module = import_module(name)
    return cast(CmdModule, module)


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
        cmd_mod = import_mod(f'{commands_module}.{name}')

        # https://github.com/wemake-services/wemake-python-styleguide/issues/2228
        if hasattr(cmd_mod, 'run'):  # noqa: WPS421
            mod[name] = cmd_mod
    return mod


def get_cli_command_modules(file_path: str) -> NestedCmdMap:
    """Return a dictionary containing the commands and subcommands for the cli.

    `file_path` is expected to be the absolute path to the __main__.py file.
    Another restriction is that the __main__.py file must have the
    `cli.commands` module as its sibling.

    Args:
        file_path: Absolute path to the `__main__.py` file.

    Returns:
        A map containing all the modules that have the commands for the cli.
    """
    root = pth.split(pth.abspath(file_path))[0]
    main_mod = pth.split(root)[1]
    cli_root = f'{main_mod}.cli'
    root_cmd = get_command_modules(root, f'{cli_root}.commands')
    mod: dict[str, CmdModule | dict[str, CmdModule]] = {}
    for key, cmd_mod in root_cmd.items():
        mod[key] = cmd_mod

    mod['.meta'] = import_mod(f'{cli_root}.commands')
    subcommands = list(iglob(f'{root}/cli/commands/*'))
    for cmd_name in subcommands:
        if cmd_name.endswith('.py') or cmd_name.endswith('__'):
            continue
        name = pth.split(cmd_name)[1]
        mod[name] = get_command_modules(root, f'{cli_root}.commands.{name}')
        mod[f'{name}.meta'] = import_mod(f'{cli_root}.commands.{name}')
    return mod
