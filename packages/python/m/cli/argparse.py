import argparse
from inspect import cleandoc
from types import MappingProxyType
from typing import Any, List, Tuple, TypeVar

import pydantic

STORE_TRUE = MappingProxyType({'action': 'store_true'})

Arg = Tuple[List[str], str, Any]

BaseModelT = TypeVar('BaseModelT', bound=pydantic.BaseModel)
MISSING = TypeVar('MISSING')


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


def argument_name(name: str) -> str:
    """Normalize an argument name.

    Args:
        name: Name of the argument.

    Returns:
        Normalized name of the argument.
    """
    return f"--{name.replace('_', '-')}"


def argument_description(
    description: str,
    default: Any | None = MISSING,
) -> str:
    """Append default value to argument description.

    Args:
        description: argument description.
        default: Argument's default value.

    Returns:
        The description of the argument.
    """
    default = f'(default: {default})' if default is not MISSING else ''
    return f'{description} {default}'.strip()


def add_model(
    parser: argparse.ArgumentParser,
    model: type[pydantic.BaseModel],
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


def namespace_to_dict(namespace: argparse.Namespace) -> dict[str, Any]:
    """Convert a namespace to a dictionary.

    Args:
        namespace: Namespace instance to convert.

    Returns:
        A dictionary generated from namespace.
    """
    dictionary = vars(namespace)
    for (key, value) in dictionary.items():
        if isinstance(value, argparse.Namespace):
            dictionary[key] = namespace_to_dict(value)
    return dictionary


def cli_options(
    model: type[BaseModelT],
    namespace: argparse.Namespace,
) -> BaseModelT:
    arg_dict = namespace_to_dict(namespace)
    return model.parse_obj(arg_dict)
