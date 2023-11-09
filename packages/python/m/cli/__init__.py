from pydantic import BaseModel

from .args import Arg, ArgProxy, Meta, RemainderArgs
from .cli import cli_integration_token, exec_cli, run_cli, run_main
from .engine.argparse import command
from .engine.sys import (
    cli_commands,
    command_group,
    import_cli_commands,
    merge_cli_commands,
    subcommands,
)
from .engine.types import (
    CliCommands,
    CommandModule,
    FuncArgs,
    MetaModule,
    add_arg,
)
from .handlers import (
    create_issue_handler,
    create_json_handler,
    create_yaml_handler,
)
from .validators import (
    env_var,
    env_var_or_empty,
    validate_file_exists,
    validate_json_payload,
    validate_payload,
)

# using as barrel file to export convenience functions
# pydantic.BaseModel has been re-exported as a convenience to not
# have so many imports in command files.
__all__ = (  # noqa: WPS410
    'cli_integration_token',
    'cli_commands',
    'subcommands',
    'command_group',
    'create_issue_handler',
    'create_json_handler',
    'create_yaml_handler',
    'command',
    'import_cli_commands',
    'add_arg',
    'validate_json_payload',
    'validate_payload',
    'validate_file_exists',
    'run_main',
    'exec_cli',
    'merge_cli_commands',
    'run_cli',
    'FuncArgs',
    'Arg',
    'ArgProxy',
    'RemainderArgs',
    'BaseModel',
    'Meta',
    'MetaModule',
    'CommandModule',
    'CliCommands',
    'env_var',
    'env_var_or_empty',
)
