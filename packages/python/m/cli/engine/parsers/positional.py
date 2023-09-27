from typing import cast

from pydantic.fields import FieldInfo

from ..misc import argument_description
from ..types import MISSING, AnyMap, FuncArgs


def should_handle(extras: AnyMap) -> bool:
    """Handle a positional field.

    Args:
        extras: A dictionary with information for a cli argument.

    Returns:
        True if it should handle the field as positional
    """
    return extras.get('positional', False) is True


def handle_field(name: str, field: FieldInfo) -> FuncArgs:
    """Treat the field as a positional field.

    Args:
        name: The name of the argument.
        field: A dictionary representation of the field.

    Returns:
        Function arguments for the parser `add_argument` method.
    """
    extras = cast(dict, field.json_schema_extra)
    default = field.default
    validator = extras.get('validator', None)
    is_required = extras.get('required', False)
    nargs = extras.get('nargs', None)
    arg_default = default if default is MISSING else repr(default)
    args: AnyMap = {
        'help': argument_description(field.description or '', arg_default),
    }
    if default is not MISSING:
        args['default'] = default

    if validator:
        args['type'] = validator

    if nargs:
        args['nargs'] = nargs
    elif not is_required:
        args['nargs'] = '?'

    return FuncArgs(args=[name], kwargs=args)
