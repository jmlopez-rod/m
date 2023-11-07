from typing import cast

from pydantic.fields import FieldInfo

from ..misc import argument_description, argument_name
from ..types import MISSING, AnyMap, FuncArgs


def handle_field(name: str, field: FieldInfo) -> FuncArgs:
    """Handle a standard field as an argument.

    Args:
        name: The name of the argument.
        field: A dictionary representation of the field.

    Returns:
        Function arguments for the parser `add_argument` method.
    """
    extras = cast(dict, field.json_schema_extra or {})
    default = field.default
    validator = extras.get('validator', None)
    required = extras.get('required', False)
    aliases = cast(list[str], extras.get('aliases', None))

    arg_default = default if default is MISSING else repr(default)
    if 'env_var' in repr(validator):
        # special case - do not repr
        arg_default = f'env.{default}'
    args: AnyMap = {
        'help': argument_description(field.description or '', arg_default),
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
