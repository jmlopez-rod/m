from inspect import cleandoc
from typing import Any, Callable, Literal

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from .engine.types import FuncArgs

_Unset: Any = PydanticUndefined


def RemainderArgs(  # noqa: N802
    *,
    help: str | None = _Unset,  # noqa: WPS125
) -> Any:
    """Provide a list of unrecognized arguments.

    This is a escape hatch and does not provide any typings. May be
    useful for commands that need to pass arguments to other commands.

    Args:
        help: Human-readable description.

    Returns:
        A new [`FieldInfo`][pydantic.fields.FieldInfo], the return annotation is
        `Any` so `Arg` can be used on type annotated fields without causing a typing error.
    """
    return FieldInfo.from_field(
        [],
        description=help,
        json_schema_extra={'__remainder_args': True},
    )


def Arg(  # noqa: N802, WPS211
    default: Any = PydanticUndefined,
    *,
    help: str,  # noqa: WPS125
    positional: bool | None = None,
    required: bool | None = None,
    aliases: list[str] | None = None,
    nargs: int | Literal['?', '*', '+'] | None = None,
    validator: Callable[[str], str] | None = None,
) -> Any:
    """Create a pydantic `Field`.

    Field docs: https://docs.pydantic.dev/2.2/usage/fields

    Defines properties used to create an argparse argument. This function
    should work for most cases. If we need something that is not covered
    we can use `ArgProxy` instead which is untyped but provides all the arguments
    and keyword arguments to argparse.

    See https://docs.python.org/3/library/argparse.html.

    Args:
        default: Default value if the field is not set.
        help: Human-readable description.
        positional: Whether the argument is positional or not.
        required: Indicate whether an argument is required or optional.
        aliases: Alternative names for the argument.
        nargs: Number of times the argument can be used.
        validator: Function to validate the argument.

    Returns:
        A new [`FieldInfo`][pydantic.fields.FieldInfo]. The return annotation is
            `Any` so `Arg` can be used on type annotated fields without causing
            a typing error.
    """
    extras = {
        'positional': positional,
        'validator': validator,
        'aliases': aliases,
        'nargs': nargs,
        'required': required,
    }
    return FieldInfo.from_field(
        default,
        description=cleandoc(help),
        json_schema_extra={k: v for k, v in extras.items() if v is not None},
    )


def ArgProxy(*args: Any, **kwargs: Any) -> Any:  # noqa: N802
    """Wrap function to provide all argparse inputs.

    This is a escape hatch and does not provide any typings.
    See https://docs.python.org/3/library/argparse.html.

    Args:
        args: The arguments to argparse add_arguments.
        kwargs: The keyword arguments to argparse add arguments.

    Returns:
        A new [`FieldInfo`][pydantic.fields.FieldInfo]. The return annotation is
            `Any` so `Arg` can be used on type annotated fields without causing
            a typing error.
    """
    return FieldInfo.from_field(
        json_schema_extra={
            'proxy': FuncArgs(args=list(args), kwargs=kwargs),
        },
    )


def Meta(  # noqa: N802
    *,
    help: str,  # noqa: WPS125
    description: str,
) -> dict[str, str]:
    """Create the meta dictionary for a subcommand description.

    In the case of the root command the `help` may be set to empty since it
    is not used.

    Args:
        help: The help message for the subcommand.
        description: The description for the command/subcommand.

    Returns:
        A dictionary with the help and description.
    """
    return {
        'help': help,
        'description': cleandoc(description),
    }
