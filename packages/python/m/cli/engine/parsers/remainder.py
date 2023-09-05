import argparse

from ..misc import argument_description
from ..types import MISSING, AnyMap, FuncArgs


def should_handle(field: AnyMap) -> bool:
    """Handle the __remainder_args field.

    Args:
        field: A dictionary with information for a cli argument.

    Returns:
        True if it should provide the remainder arguments.
    """
    return field.get('__remainder_args') is True


def handle_field(name: str, field: AnyMap) -> FuncArgs:
    """Set the remainder arguments.

    Args:
        name: The name of the field.
        field: A dictionary representation of the field.

    Returns:
        Function arguments for the parser `add_argument` method.
    """
    args: AnyMap = {
        'help': argument_description(field['description'], MISSING),
        'nargs': argparse.REMAINDER,
    }
    return FuncArgs(args=[name], kwargs=args)
