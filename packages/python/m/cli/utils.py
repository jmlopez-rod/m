import argparse
import json
import sys
from contextlib import suppress
from typing import Any, Callable, Optional, cast

from m.core import Issue, OneOf
from m.core.ci_tools import error_block, get_ci_tool

from ..core.io import env
from .engine.misc import params_count
from .engine.sys import get_cli_command_modules
from .engine.types import CmdMap, CommandModule, MetaMap, NestedCmdMap
from .validators import validate_non_empty_str


def _main_parser(
    mod: NestedCmdMap,
    meta: MetaMap,
    add_args: Callable[[argparse.ArgumentParser], None] | None = None,
) -> argparse.Namespace:
    main_meta = meta['_root'].meta
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
        if isinstance(mod[name], dict):
            meta_mod = meta[name]
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
            sub_mod = cast(CmdMap, mod[name])
            for subname in sorted(sub_mod.keys()):
                run_func = sub_mod[subname].run
                if params_count(run_func) == 2:
                    run_func(None, subsubp)
        else:
            mod_inst = cast(CommandModule, mod[name])
            run_func = mod_inst.run
            if params_count(run_func) == 2:
                run_func(None, subp)
    return argp.parse_args()


def run_cli(
    file_path: str,
    add_args: Callable[[argparse.ArgumentParser], None] | None = None,
) -> None:
    """Run the cli application.

    usage::

        def add_args(argp):
            argp.add_argument(...)
        def main():
            run_cli(__file__, add_args)

    We only need `add_args` if we need to gain access to the
    `argparse.ArgumentParser` instance.

    Args:
        file_path: The full name of the file: __file__.
        add_args: Optional callback to gain access to the ArgumentParser.
    """
    mod, meta = get_cli_command_modules(file_path)
    arg = _main_parser(mod, meta, add_args)

    run_func = None

    if hasattr(arg, 'subcommand_name'):
        sub_mod = cast(CmdMap, mod[arg.command_name])
        run_func = sub_mod[arg.subcommand_name].run
    else:
        run_func = cast(CommandModule, mod[arg.command_name]).run

    len_run_args = params_count(run_func)
    run_args = [arg, None][:len_run_args]
    # mypy is having a hard time figuring out the type of run_args
    exit_code = run_func(*run_args)  # type:ignore[arg-type]
    sys.exit(exit_code)


def display_issue(issue: Issue) -> None:
    """Print an error message.

    The error message is customize to the CI environment.

    Args:
        issue: An instance of an Issue.
    """
    get_ci_tool().error(issue.message)
    error_block(str(issue))


def display_result(inst: Any) -> None:
    """Print the JSON stringification of a non-None parameter.

    Args:
        inst: The instance to stringify.
    """
    if inst is not None:
        msg = inst
        with suppress(Exception):
            msg = json.dumps(inst, separators=(',', ':'))
        print(msg)  # noqa: WPS421


def run_main(
    callback: Callable[[], OneOf[Issue, Any]],
    handle_result: Callable[[Any], None] = display_result,
    handle_issue: Callable[[Issue], None] = display_issue,
) -> int:
    """Run the callback and print the returned value.

    To change how the result or an issue should be display provide the optional
    arguments `handle_result` and `handle_issue`. For instance, to display the
    raw value provide the `print` function.

    Args:
        callback: A function that returns a `OneOf`.
        handle_result: A function that takes in the Good result.
        handle_issue: A function that takes in the Issue.

    Returns:
        0 if the callback is a `Good` result otherwise return 1.
    """
    try:
        res = callback()
        result_value = res.value
        if res.is_bad:
            if isinstance(result_value, Issue):
                handle_issue(result_value)
            else:
                issue = Issue(
                    'non-issue exception',
                    cause=cast(Issue, result_value),
                )
                handle_issue(issue)
            return 1
        handle_result(result_value)
    except Exception as ex:
        issue = Issue('unknown caught exception', cause=ex)
        handle_issue(issue)
        return 1
    return 0


def error(msg: str, issue: Optional[Issue] = None) -> int:
    """Print an error message.

    Args:
        msg: The error message.
        issue: Optional `Issue` instance to go along with the error message.

    Returns:
        The integer 1.
    """
    get_ci_tool().error(msg)
    if issue:
        error_block(str(issue), sys.stderr)
    return 1


def cli_integration_token(
    integration: str,
    env_var: str,
) -> Callable[[argparse.ArgumentParser], argparse.Action]:
    """Return a function that takes in a parser.

    This generated function registers a token argument in the parser
    which looks for its value in the environment variables.

    Args:
        integration: The name of the integration.
        env_var: The environment variable name.

    Returns:
        A function that
    """
    return lambda parser: parser.add_argument(
        '-t',
        '--token',
        type=validate_non_empty_str,
        default=env(env_var),
        help=f'{integration} access token (default: env.{env_var})',
    )
