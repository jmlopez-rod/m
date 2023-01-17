import argparse
from functools import partial
from typing import Callable, TypeVar

from pydantic import BaseModel

from .engine.misc import namespace_to_dict, params_count
from .engine.parsers import boolean, positional, proxy, standard
from .engine.types import AnyMap, CommandInputs, FuncArgs

BaseModelT = TypeVar('BaseModelT', bound=BaseModel)


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
    schema = model.schema()
    parser.description = schema['description']
    parser.formatter_class = argparse.RawTextHelpFormatter
    for name, field in schema['properties'].items():
        arg_inputs = _parse_field(name, field)
        parser.add_argument(*arg_inputs.args, **arg_inputs.kwargs)


def cli_options(
    model: type[BaseModelT],
    namespace: argparse.Namespace,
) -> BaseModelT:
    arg_dict = namespace_to_dict(namespace)
    return model.parse_obj(arg_dict)


def _run_wrapper(
    run_func: Callable[..., int],
    cmd_inputs: CommandInputs,
    arg: argparse.Namespace | None,
    parser: argparse._SubParsersAction | None,  # noqa: WPS437
) -> int:
    if parser:
        sub_parser = parser.add_parser(cmd_inputs.name, help=cmd_inputs.help)
        add_model(sub_parser, cmd_inputs.model)
        return 0
    if isinstance(arg, argparse.Namespace):
        opt = cli_options(cmd_inputs.model, arg)
        len_run_params = params_count(run_func)
        if len_run_params == 2:
            return run_func(opt, arg)
        if len_run_params == 1:
            return run_func(opt)
        return run_func()
    raise NotImplementedError('m dev error: provide either arg or parser')


def handle_decorated_func(
    cmd_inputs: CommandInputs,
    func: Callable,
):
    return partial(_run_wrapper, func, cmd_inputs)


def command(
    name: str,
    help: str,  # noqa: WPS125
    model: type[BaseModel],
):
    return partial(handle_decorated_func, CommandInputs(name, help, model))
