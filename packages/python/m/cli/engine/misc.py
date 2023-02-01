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


def argument_name(name: str) -> str:
    """Normalize an argument name.

    Args:
        name: Name of the argument.

    Returns:
        Normalized name of the argument.
    """
    cli_arg_name = name.replace('_', '-')
    dashes = '-' if len(cli_arg_name) == 1 else '--'
    return f'{dashes}{cli_arg_name}'


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
