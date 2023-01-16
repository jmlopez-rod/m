import argparse
from functools import partial
from inspect import cleandoc
from types import MappingProxyType
from typing import Any, Callable, List, Tuple, TypeVar

from pydantic import BaseModel

from .engine.misc import (
    argument_description,
    argument_name,
    namespace_to_dict,
    params_count,
)
from .engine.types import MISSING

STORE_TRUE = MappingProxyType({'action': 'store_true'})

Arg = Tuple[List[str], str, Any]

BaseModelT = TypeVar('BaseModelT', bound=BaseModel)


def add_arguments(
    parser: argparse.ArgumentParser,
    args: Tuple[Arg, ...],
) -> None:
    """Add arguments to the parser.

    Args:
        parser:
            An argparse ArgumentParser instance.
        args:
            A list of arguments. Each entry is composed of 3 items:
                - The names of the arguments ([-s, '--long'])
                - The help string (may be multilined)
                - A dictionary with extra options to `add_argument`.
    """
    for names, help_str, extra in args:
        parser.add_argument(*names, help=cleandoc(help_str), **extra)


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
        field_default = field.get('default', MISSING)
        is_positional = field.get('positional', False)
        field_type = field.get('type', None)
        args: dict[str, Any] = {
            'help': argument_description(
                field['description'],
                MISSING if field_type == 'boolean' else field_default,
            ),
        }
        _add_validator(args, field)

        if is_positional:
            _handle_positional(args, field)
        else:
            field_name = argument_name(name)
            args['required'] = field.get('required', False)
            args['type'] = str

        field_name = name
        if field_type == 'boolean':
            field_name = _handle_boolean(args, field, name)
        parser.add_argument(field_name, **args)


def _add_validator(args: dict, field: dict) -> None:
    if field.get('validator', None):
        args['type'] = field['validator']


def _handle_positional(args: dict, field: dict) -> None:
    is_required = field.get('required', False)
    if not is_required:
        args['nargs'] = '?'


def _handle_boolean(args: dict, field: dict, name: str) -> str:
    args.pop('type')
    if field.get('default', False):
        args['action'] = 'store_false'
        args['dest'] = name
        return argument_name(f'no-{name}')
    args['action'] = 'store_true'
    return argument_name(name)


def cli_options(
    model: type[BaseModelT],
    namespace: argparse.Namespace,
) -> BaseModelT:
    arg_dict = namespace_to_dict(namespace)
    return model.parse_obj(arg_dict)


def run_wrapper(
    arg: argparse.Namespace | None,
    parser: argparse._SubParsersAction | None,
    run_func: Callable,
    name: str,
    help: str,  # noqa: WPS125
    model: type[BaseModel],
) -> int:
    if parser:
        subp = parser.add_parser(name, help=help)
        add_model(subp, model)
        return 0
    opt = cli_options(model, arg)
    len_run_params = params_count(run_func)
    if len_run_params == 2:
        return run_func(opt, arg)
    elif len_run_params == 1:
        return run_func(opt)
    return run_func()

def command(
    name: str,
    help: str,  # noqa: WPS125
    model: type[BaseModel],
):
    def inner(run_func):
        # return partial(run_wrapper, name=name, help=help, model=model, run_func=run_func)
        def wrapper(
            arg: argparse.Namespace | None,
            parser: argparse._SubParsersAction | None = None,
        ) -> int:
            if parser:
                subp = parser.add_parser(name, help=help)
                add_model(subp, model)
                return 0
            opt = cli_options(model, arg)
            len_run_params = params_count(run_func)
            if len_run_params == 2:
                return run_func(opt, arg)
            elif len_run_params == 1:
                return run_func(opt)
            return run_func()
        return wrapper
    return inner
