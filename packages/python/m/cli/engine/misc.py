import argparse
from inspect import signature
from typing import Any, Callable

from .types import MISSING


def params_count(func: Callable) -> int:
    """Compute the number of parameters in a function.

    Args:
        func: The function in question.

    Returns:
        the number of parameters.
    """
    sig = signature(func)
    return len(sig.parameters)


def namespace_to_dict(namespace: argparse.Namespace) -> dict[str, Any]:
    """Convert a namespace to a dictionary.

    Args:
        namespace: Namespace instance to convert.

    Returns:
        A dictionary generated from namespace.
    """
    dictionary = namespace.__dict__
    for (key, arg_value) in dictionary.items():
        if isinstance(arg_value, argparse.Namespace):
            dictionary[key] = namespace_to_dict(arg_value)
    return dictionary


def argument_name(name: str) -> str:
    """Normalize an argument name.

    Args:
        name: Name of the argument.

    Returns:
        Normalized name of the argument.
    """
    cli_arg_name = name.replace('_', '-')
    return f'--{cli_arg_name}'


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
