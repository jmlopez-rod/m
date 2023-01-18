import argparse
import json
import sys
from typing import Any, Callable, Optional, cast

from ..core.fp import OneOf
from ..core.io import CiTool, env, error_block
from ..core.issue import Issue
from .engine.misc import params_count
from .engine.sys import get_cli_command_modules
from .engine.types import CmdMap, CommandModule, NestedCmdMap
from .validators import validate_non_empty_str


def main_parser(
    mod: NestedCmdMap,
    add_args: Callable[[argparse.ArgumentParser], None] | None = None,
):
    """Create an argp and return the result calling its parse_arg method.

    The `add_args` param may be provided as a function that takes in an
    `argparse.ArgumentParser` instance to be able to take additional
    actions.
    """
    meta_mod = cast(CommandModule, mod['.meta'])
    main_meta = meta_mod.meta  # type: ignore
    raw = argparse.RawTextHelpFormatter
    # NOTE: In the future we will need to extend from this class to be able to
    #   override the error method to be able to print CI environment messages.
    argp = argparse.ArgumentParser(
        formatter_class=raw,
        description=main_meta['description'] if main_meta else '...',
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
            meta_mod = cast(CommandModule, mod[f'{name}.meta'])
            meta = meta_mod.meta or {}
            parser = subp.add_parser(
                name,
                help=meta['help'],
                formatter_class=raw,
                description=meta['description'],
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
            sub_mod = cast(CmdMap, mod[name])
            for subname in sorted(sub_mod.keys()):
                run_func = sub_mod[subname].run
                add_parser = sub_mod[subname].add_parser
                if params_count(run_func) == 2:
                    run_func(None, subsubp)
                elif add_parser:
                    add_parser(subsubp, raw)
        else:
            mod_inst = cast(CommandModule, mod[name])
            run_func = mod_inst.run
            add_parser = mod_inst.add_parser
            if params_count(run_func) == 2:
                run_func(None, subp)
            elif add_parser:
                add_parser(subp, raw)
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

    run_func = None

    if hasattr(arg, 'subcommand_name'):
        sub_mod = cast(CmdMap, mod[arg.command_name])
        run_func = sub_mod[arg.subcommand_name].run
    else:
        run_func = cast(CommandModule, mod[arg.command_name]).run

    len_run_args = params_count(run_func)
    run_args = [arg, None][:len_run_args]
    sys.exit(run_func(*run_args))


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
    print_raw param to True to bypass the JSON stringification. To change how
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
