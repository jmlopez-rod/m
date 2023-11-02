import argparse as ap
from dataclasses import dataclass
from typing import Any, Callable

import typing_extensions
from pydantic import BaseModel
from pydantic_core import PydanticUndefined


@dataclass
class CommandInputs:
    """Inputs to command decorator."""

    help: str

    model: type[BaseModel]


@dataclass
class FuncArgs:
    """Stores function arguments."""

    args: list[Any]
    kwargs: dict[str, Any]


@typing_extensions.deprecated(
    'The `add_arg` method is deprecated; use `m.cli.ArgProxy` instead.',
)
def add_arg(*args: Any, **kwargs: Any) -> FuncArgs:
    """Wrap FuncArgs arguments in a function.

    Args:
        args: The arguments to argparse add_arguments.
        kwargs: The keyword arguments to argparse add arguments.

    Returns:
        A FuncArgs instance.
    """
    # `m` does not reference this function anymore, excluding from coverage
    return FuncArgs(args=list(args), kwargs=kwargs)  # pragma: no cover


# This is the actual signature of the run function after the `command`
# annotation is set on it.
DecoratedRunFunction = Callable[
    [str, ap.Namespace | None, ap._SubParsersAction | None],  # noqa: WPS437, WPS465 # pylint:disable=protected-access
    int,
]


@dataclass
class CommandModule:
    """Container to store the run function from a "command" module."""

    run: DecoratedRunFunction


CommandModuleMap = dict[str, CommandModule]


@dataclass
class MetaModule:
    """Container to store a metadata dictionary from a "meta" module."""

    meta: dict[str, str]
    add_arguments: Callable[[ap.ArgumentParser], None] | None = None


@dataclass
class CliSubcommands:
    """Container to store subcommands."""

    # Dictionary of subcommands.
    subcommands: CommandModuleMap

    # Each subcommand needs to provide metadata to create the help message.
    meta: MetaModule | None


@dataclass
class CliCommands:
    """Container to store the commands and subcommands for the cli."""

    commands: dict[str, CommandModule | CliSubcommands]

    # Optional root meta data to provide information about the cli.
    meta: MetaModule | None


MISSING = PydanticUndefined
AnyMap = dict[str, Any]
