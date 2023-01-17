from typing import cast

from ..misc import argument_description, argument_name
from ..types import MISSING, AnyMap, FuncArgs


def handle_field(name: str, field: AnyMap) -> FuncArgs:
    """Handle a standard field as an argument.

    Args:
        name: The name of the argument.
        field: A dictionary representation of the field.

    Returns:
        Function arguments for the parser `add_argument` method.
    """
    default = field.get('default', MISSING)
    validator = field.get('validator', None)
    required = field.get('required', False)
    aliases = cast(list[str], field.get('aliases', None))

    arg_default = default if default is MISSING else repr(default)
    args: AnyMap = {
        'help': argument_description(field['description'], arg_default),
        'required': required,
        'type': str,
    }

    if default is not MISSING:
        args['default'] = default

    if validator:
        args['type'] = validator

    names = [argument_name(name)]
    if aliases:
        names = [argument_name(alias) for alias in aliases]

    return FuncArgs(args=names, kwargs=args)
