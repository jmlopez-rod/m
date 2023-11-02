from dataclasses import dataclass
from typing import Any, cast

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

AnyMap = dict[str, Any]
MISSING = PydanticUndefined
NO_HELP = '...'


@dataclass
class CliArgs:
    """Stores cli arguments names."""

    positional: list[str]
    optional: list[str]
    required: list[str]


@dataclass
class FuncArgs:
    """Stores function arguments."""

    args: list[Any]
    kwargs: dict[str, Any]


class ArgParseInfo(BaseModel):
    """Information about an argparse argument."""

    description: str
    option_names: list[str]
    choices: None | list[str]
    default_value: None | str
    required: bool = False
    positional: bool = False


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


def _parse_info_bool(name: str, field: FieldInfo) -> ArgParseInfo:
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
    if default:
        names = [argument_name(f'no-{name}')]
        if aliases:
            names = [argument_name(f'no-{alias}') for alias in aliases]
    else:
        names = [argument_name(name)]
        if aliases:
            names = [argument_name(alias) for alias in aliases]

    return ArgParseInfo(
        description=field.description or '',
        option_names=names,
        choices=None,
        default_value=str(bool(default)).lower(),
    )


def _parse_info_standard(name: str, field: FieldInfo) -> ArgParseInfo:
    extras = cast(dict, field.json_schema_extra or {})
    default = field.default
    required = extras.get('required', False)
    aliases = cast(list[str], extras.get('aliases', None))
    validator = extras.get('validator')
    default = None if default is MISSING else repr(default)
    if 'env_var' in repr(validator):
        # special case - do not repr
        default = f'env.{field.default}'

    names = [argument_name(name)]
    if aliases:
        names = [argument_name(alias) for alias in aliases]

    return ArgParseInfo(
        description=field.description or NO_HELP,
        option_names=names,
        choices=None,
        default_value=default,
        required=required,
    )


def parse_field(name: str, field: FieldInfo) -> ArgParseInfo:
    """Process a pydantic field.

    Args:
        name: The name of the argument.
        field: A pydantic `FieldInfo` object.

    Raises:
        NotImplementedError: If `json_schema_extra` is not a dict.

    Returns:
        A `ArgParseInfo` object that can be used to create documentation for
            the argument.
    """
    extras = field.json_schema_extra
    default = field.default
    if not isinstance(extras, dict):  # pragma: no cover
        not_supported = 'json_schema_extra only supported as a dict'
        raise NotImplementedError(not_supported)
    if extras.get('positional', False) is True:
        return ArgParseInfo(
            description=field.description or NO_HELP,
            option_names=[name],
            choices=None,
            default_value=None if default is MISSING else repr(default),
            positional=True,
        )
    if field.annotation is bool:
        return _parse_info_bool(name, field)
    if extras.get('proxy', None) is not None:
        proxy = cast(FuncArgs, extras['proxy'])
        default = proxy.kwargs.get('default', None)
        validator = proxy.kwargs.get('type')
        if 'env_var' in repr(validator):
            default = f'env.{default}'
        return ArgParseInfo(
            description=proxy.kwargs.get('help', NO_HELP),
            option_names=proxy.args,
            choices=proxy.kwargs.get('choices', None),
            default_value=default,
        )
    if extras.get('__remainder_args') is True:
        return ArgParseInfo(
            description=field.description or NO_HELP,
            option_names=[name],
            choices=None,
            default_value=None if default is MISSING else repr(default),
        )
    return _parse_info_standard(name, field)
