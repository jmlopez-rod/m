import argparse
from functools import partial
from inspect import cleandoc
from typing import Callable
from warnings import warn

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from .misc import params_count
from .parsers import boolean, positional, proxy, remainder, standard
from .types import CommandInputs, FuncArgs


def _parse_field(name: str, field: FieldInfo) -> FuncArgs:
    extras = field.json_schema_extra
    if not isinstance(extras, dict):  # pragma: no cover
        # We can go out of our way to not make it a dict but then that's on the
        # developer. Won't handle the case that json_schema_extra is a function.
        not_supported = 'json_schema_extra only supported as a dict'
        raise NotImplementedError(not_supported)
    if positional.should_handle(extras):
        return positional.handle_field(name, field)
    if field.annotation is bool:
        return boolean.handle_field(name, field)
    if proxy.should_handle(extras):
        return proxy.handle_field(extras)
    if remainder.should_handle(extras):
        return remainder.handle_field(name, field)
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
    parser.description = cleandoc(model.__doc__ or '')
    parser.formatter_class = argparse.RawTextHelpFormatter
    for name, field in model.model_fields.items():
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
