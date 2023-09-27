from typing import cast

from ..types import AnyMap, FuncArgs


def should_handle(extras: AnyMap) -> bool:
    """Handle the proxy field.

    Args:
        extras: A dictionary with information for a cli argument.

    Returns:
        True if it should handle the field as a proxy to the parser.
    """
    return extras.get('proxy', None) is not None


def handle_field(extras: AnyMap) -> FuncArgs:
    """Pass the `proxy` property in the field as is.

    Args:
        extras: A dictionary representation of the field.

    Returns:
        Function arguments for the parser `add_argument` method.
    """
    # proxy field is expected to be a FuncArgs instance.
    return cast(FuncArgs, extras['proxy'])
