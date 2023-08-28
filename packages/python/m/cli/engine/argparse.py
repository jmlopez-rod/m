import argparse
from functools import partial
from typing import Callable
from warnings import warn

from pydantic import BaseModel

from .misc import params_count
from .parsers import boolean, positional, proxy, standard
from .types import AnyMap, CommandInputs, FuncArgs


def _parse_field(name: str, field: AnyMap) -> FuncArgs:
    if positional.should_handle(field):
        return positional.handle_field(name, field)
    if boolean.should_handle(field):
        return boolean.handle_field(name, field)
    if proxy.should_handle(field):
        return proxy.handle_field(field)
    return standard.handle_field(name, field)


def add_model(
    parser: argparse.ArgumentParser,
    model: type[BaseModel],
) -> None:
    """Add a pydantic model to an argparse ArgumentParser.

    Args:
        parser: The ArgumentParser instance.
        model: The pydantic model declaring the cli options.
    """
    schema = model.model_json_schema()
    parser.description = schema['description']
    parser.formatter_class = argparse.RawTextHelpFormatter
    for name, field in schema['properties'].items():
        arg_inputs = _parse_field(name, field)
        parser.add_argument(*arg_inputs.args, **arg_inputs.kwargs)


def _run_wrapper(
    run_func: Callable[..., int],
    cmd_inputs: CommandInputs,
    cmd_name: str,
    arg: argparse.Namespace | None,
    parser: argparse._SubParsersAction | None,  # noqa: WPS437
) -> int:
    if parser:
        sub_parser = parser.add_parser(cmd_name, help=cmd_inputs.help)
        add_model(sub_parser, cmd_inputs.model)
        return 0
    if isinstance(arg, argparse.Namespace):
        arg_dict = arg.__dict__
        opt = cmd_inputs.model.model_validate(arg_dict)
        len_run_params = params_count(run_func)
        args = [opt, arg][:len_run_params]
        return run_func(*args)
    # Should not be reachable during a normal run - only checking
    # to make sure we provide at least one argument.
    raise NotImplementedError(  # pragma: no cover
        'm dev error: provide either arg or parser',
    )


def _handle_decorated_func(cmd_inputs: CommandInputs, func: Callable):
    return partial(_run_wrapper, func, cmd_inputs)


def command(
    *,
    help: str,  # noqa: WPS125
    model: type[BaseModel],
    name: str | None = None,
) -> partial[partial[int]]:
    """Apply a decorator to the `run` function to make it into a command.

    Args:
        name: The command name.
        help: A short description of the command.
        model: A pydantic model to describe the cli arguments.

    Returns:
        A transformed run function aware of the arguments model.
    """
    # m no longer uses the name argument but we keep it for now
    if name:  # pragma: no cover
        warn('`name` is no longer needed, please remove it', DeprecationWarning)
    return partial(_handle_decorated_func, CommandInputs(help, model))
