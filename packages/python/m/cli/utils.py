import argparse
import json
import os.path as pth
import sys
from glob import iglob
from typing import Any, Callable, Dict
from typing import MutableMapping as Map
from typing import Optional, Type, Union, cast

from ..core.fp import OneOf
from ..core.io import CiTool, env, error_block
from ..core.issue import Issue
from .validators import validate_non_empty_str


class CmdModule:
    """Interface for command modules."""

    meta: Dict[str, str]

    @staticmethod
    def add_arguments(_parser: argparse.ArgumentParser) -> None:
        """Define options that may apply to the subparsers.

        Should be defined if we want to manipulate the argument parser
        object.
        """
        ...

    @staticmethod
    def add_parser(
        _subparser: argparse._SubParsersAction,  # noqa pylint: disable=protected-access
        _raw: Type[argparse.RawTextHelpFormatter],
    ) -> None:
        """Define cli arguments for a command."""
        ...

    @staticmethod
    def run(_arg: argparse.Namespace) -> int:
        """Entry point for the cli.

        Call a library function and return 0 if successful or non-zero if there
        is a failure.
        """
        ...


def import_mod(name: str) -> CmdModule:
    """Import a module by string."""
    module = __import__(name)
    for part in name.split('.')[1:]:
        module = getattr(module, part)
    return cast(CmdModule, module)


def get_command_modules(
    root: str,
    commands_module: str,
) -> Map[str, CmdModule]:
    """Return a dictionary mapping command names to modules that define an
    `add_parser` method.

    root: The absolute path of the directory containing the __main__.py that
          activates the cli.
    commands_module: The full module resolution. For instance `m.cli.commands`.
    """
    dir_name = '/'.join(commands_module.split('.')[1:])
    mod_names = list(iglob(f'{root}/{dir_name}/*.py'))
    mod = {}
    for name in mod_names:
        tname = pth.split(name)[1][:-3]
        tmod = import_mod(f'{commands_module}.{tname}')
        if hasattr(tmod, 'add_parser'):
            mod[tname] = tmod
    return mod


def get_cli_command_modules(
    file_path: str,
) -> Map[str, Union[CmdModule, Map[str, CmdModule]]]:
    """Return a dictionary containing the commands and subcommands for the cli.

    Note that file_path is expected to be the absolute path to the
    __main__.py file. Another restriction is that the __main__.py file
    must have the `cli.commands` module as its sibling.
    """
    root = pth.split(pth.abspath(file_path))[0]
    main_mod = pth.split(root)[1]
    cli_root = f'{main_mod}.cli'
    root_cmd = get_command_modules(root, f'{cli_root}.commands')
    mod: Map[str, Union[CmdModule, Map[str, CmdModule]]] = {}
    for key, val in root_cmd.items():
        mod[key] = val

    mod['.meta'] = import_mod(f'{cli_root}.commands')
    subcommands = list(iglob(f'{root}/cli/commands/*'))
    for name in subcommands:
        if name.endswith('.py') or name.endswith('__'):
            continue
        tname = pth.split(name)[1]
        mod[tname] = get_command_modules(root, f'{cli_root}.commands.{tname}')
        mod[f'{tname}.meta'] = import_mod(f'{cli_root}.commands.{tname}')
    return mod


def main_parser(
    mod: Map[str, Union[CmdModule, Map[str, CmdModule]]],
    add_args=None,
):
    """Creates an argp parser and returns the result calling its parse_arg
    method.

    The `add_args` param may be provided as a function that takes in an
    `argparse.ArgumentParser` instance to be able to take additional
    actions.
    """
    meta_mod = cast(CmdModule, mod['.meta'])
    main_meta = meta_mod.meta  # type: ignore
    raw = argparse.RawTextHelpFormatter
    # NOTE: In the future we will need to extend from this class to be able to
    #   override the error method to be able to print CI environment messages.
    argp = argparse.ArgumentParser(
        formatter_class=raw,
        description=main_meta['description'],
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
    names = sorted(mod.keys())
    for name in names:
        if name.endswith('.meta'):
            continue
        if isinstance(mod[name], dict):
            meta_mod = cast(CmdModule, mod[f'{name}.meta'])
            meta = meta_mod.meta  # type: ignore
            parser = subp.add_parser(
                name,
                help=meta['help'],
                formatter_class=raw,
                description=meta['description'],
            )
            if hasattr(meta_mod, 'add_arguments'):
                meta_mod.add_arguments(parser)
            subsubp = parser.add_subparsers(
                title='commands',
                dest='subcommand_name',
                required=True,
                help='additional help',
                metavar='<command>',
            )
            sub_mod = cast(Dict[str, CmdModule], mod[name])
            for subname in sorted(sub_mod.keys()):
                sub_mod[subname].add_parser(subsubp, raw)
        else:
            cast(CmdModule, mod[name]).add_parser(subp, raw)
    return argp.parse_args()


def run_cli(
    file_path: str,
    main_args=None,
) -> None:
    """Helper function to create a cli application.

        def main_args(argp):
            argp.add_argument(...)
        def main():
            run_cli(__file__, main_args)

    We only need `main_args` if we need to gain access to the
    `argparse.ArgumentParser` instance.
    """
    mod = get_cli_command_modules(file_path)
    arg = main_parser(mod, main_args)
    if hasattr(arg, 'subcommand_name'):
        sub_mod = cast(Dict[str, CmdModule], mod[arg.command_name])
        sys.exit(sub_mod[arg.subcommand_name].run(arg))
    else:
        sys.exit(cast(CmdModule, mod[arg.command_name]).run(arg))


def display_issue(issue: Issue) -> None:
    """print an error message."""
    CiTool.error(issue.message)
    error_block(str(issue))


def display_result(val: Any) -> None:
    """print the JSON stringification of the param `val` provided that val is
    not `None`."""
    if val is not None:
        try:
            print(json.dumps(val, separators=(',', ':')))
        except Exception:
            print(val)


def run_main(
    callback: Callable[[], OneOf[Issue, Any]],
    handle_result: Callable[[Any], None] = display_result,
    handle_issue: Callable[[Issue], None] = display_issue,
):
    """Run the callback and print the returned value as a JSON string. Set the
    print_raw param to True to bypass the JSON stringnification. To change how
    the result or an issue should be display then provide the optional
    arguments handle_result and handle_issue. For instance, to display the raw
    value simply provide the `print` function.

    Return 0 if the callback is a `Good` result otherwise return 1.
    """
    try:
        res = callback()
        val = res.value
        if res.is_bad:
            if isinstance(val, Issue):
                handle_issue(val)
            else:
                issue = Issue('non-issue exception', cause=cast(Issue, val))
                handle_issue(issue)
            return 1
        handle_result(val)
    except Exception as ex:
        issue = Issue('unknown caught exception', cause=ex)
        handle_issue(issue)
        return 1
    return 0


def call_main(fun, args, print_raw=False) -> int:
    """
    @deprecated: Use run_main

    The `fun` param will be called by providing the list of values in
    `args`. By default, the result of calling `fun` will be JSON stringified
    but we can avoid this by providing `print_raw` set to True. """
    try:
        res = fun(*args)
        val = res.value
        if res.is_bad:
            if isinstance(val, Issue):
                return error(val.message, val)
            issue = Issue('non-issue exception', cause=val)
            return error(issue.message, issue)
        if val is not None or isinstance(val, list):
            if print_raw:
                print(val)
            else:
                try:
                    print(json.dumps(val, separators=(',', ':')))
                except Exception:
                    print(val, file=sys.stderr)
    except Exception as ex:
        CiTool.error('unknown caught exception')
        error_block(repr(ex))
        return 1
    return 0


def error(msg: str, issue: Optional[Issue] = None) -> int:
    """print an error message."""
    CiTool.error(msg)
    if issue:
        error_block(str(issue))
    return 1


def cli_integration_token(integration: str, env_var: str):
    """Return a function that takes in a parser.

    This generated function registers a token argument in the parser
    which looks for its value in the environment variables.
    """
    return lambda parser: parser.add_argument(
        '-t',
        '--token',
        type=validate_non_empty_str,
        default=env(env_var),
        help=f'{integration} access token (default: env.{env_var})',
    )
