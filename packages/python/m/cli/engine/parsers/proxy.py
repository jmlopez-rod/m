from typing import cast

from ..types import AnyMap, FuncArgs


def should_handle(field: AnyMap) -> bool:
    """Handle the proxy field.

    Args:
        field: A dictionary with information for a cli argument.

    Returns:
        True if it should handle the field as a proxy to the parser.
    """
    return field.get('proxy', None) is not None


def handle_field(field: AnyMap) -> FuncArgs:
    """Pass the `proxy` property in the field as is.

    Args:
        field: A dictionary representation of the field.

    Returns:
        Function arguments for the parser `add_argument` method.
    """
    # relying on documentation to state that `proxy` should be used to provide
    # the arguments.
    return cast(FuncArgs, field['proxy'])
