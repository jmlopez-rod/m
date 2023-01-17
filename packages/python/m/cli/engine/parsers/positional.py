from ..misc import argument_description
from ..types import MISSING, AnyMap, FuncArgs


def should_handle(field: AnyMap) -> bool:
    """Handle a positional field.

    Args:
        field: A dictionary with information for a cli argument.

    Returns:
        True if it should handle the field as positional
    """
    return field.get('positional', False) is True


def handle_field(name: str, field: AnyMap) -> FuncArgs:
    """Treat the field as a positional field.

    Args:
        name: The name of the argument.
        field: A dictionary representation of the field.

    Returns:
        Function arguments for the parser `add_argument` method.
    """
    default = field.get('default', MISSING)
    validator = field.get('validator', None)
    is_required = field.get('required', False)
    nargs = field.get('nargs', None)

    arg_default = default if default is MISSING else repr(default)
    args: AnyMap = {
        'help': argument_description(field['description'], arg_default),
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
