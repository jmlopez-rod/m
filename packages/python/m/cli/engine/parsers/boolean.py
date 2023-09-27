from typing import cast

from pydantic.fields import FieldInfo

from ..misc import argument_description, argument_name
from ..types import MISSING, AnyMap, FuncArgs


def handle_field(name: str, field: FieldInfo) -> FuncArgs:
    """Treat the field as a boolean field.

    Args:
        name: The name of the argument.
        field: A dictionary representation of the field.

    Returns:
        Function arguments for the parser `add_argument` method.
    """
    default = field.default
    extras = cast(dict, field.json_schema_extra or {})
    aliases = cast(list[str], extras.get('aliases', None))
    args: AnyMap = {
        'help': argument_description(field.description or '', MISSING),
        'required': extras.get('required', False),
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
