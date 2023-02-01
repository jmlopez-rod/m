from typing import cast

from ..misc import argument_description, argument_name
from ..types import MISSING, AnyMap, FuncArgs


def should_handle(field: AnyMap) -> bool:
    """Handle a boolean argument.

    Args:
        field: A dictionary with information for a cli argument.

    Returns:
        True if it should handle the field as a boolean
    """
    return str(field.get('type', '')) == 'boolean'


def handle_field(name: str, field: AnyMap) -> FuncArgs:
    """Treat the field as a boolean field.

    Args:
        name: The name of the argument.
        field: A dictionary representation of the field.

    Returns:
        Function arguments for the parser `add_argument` method.
    """
    default = field.get('default', MISSING)
    aliases = cast(list[str], field.get('aliases', None))
    args: AnyMap = {
        'help': argument_description(field['description'], MISSING),
        'required': field.get('required', False),
    }

    if default:
        args['action'] = 'store_false'
        args['dest'] = name
        names = [argument_name(f'no-{name}')]
        if aliases:
            names = [argument_name(f'no-{alias}') for alias in aliases]
    else:
        args['action'] = 'store_true'
        names = [argument_name(name)]
        if aliases:
            names = [argument_name(alias) for alias in aliases]

    return FuncArgs(args=names, kwargs=args)
