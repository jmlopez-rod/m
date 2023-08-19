import argparse as ap
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

import typing_extensions
from pydantic import BaseModel


@dataclass
class CommandInputs:
    """Inputs to command decorator."""

    name: str
    help: str
    model: type[BaseModel]


@dataclass
class FuncArgs:
    """Stores function arguments."""

    args: list[Any]
    kwargs: dict[str, Any]


@typing_extensions.deprecated(
    'The `add_arg` method is deprecated; use `m.cli.ArgProxy` instead.'
)
def add_arg(*args, **kwargs) -> FuncArgs:
    """Wrap FuncArgs arguments in a function.

    Args:
        args: The arguments to argparse add_arguments.
        kwargs: The keyword arguments to argparse add arguments.

    Returns:
        A FuncArgs instance.

   """
    # `m` does not reference this function anymore, excluding from coverage
    return FuncArgs(args=list(args), kwargs=kwargs)  # pragma: no cover


@dataclass
class CommandModule:
    """Container to store the run function from a "command" module."""

    run: Callable[
        [ap.Namespace | None, ap._SubParsersAction | None],  # noqa: WPS437
        int,
    ]


@dataclass
class MetaModule:
    """Container to store a metadata dictionary from a "meta" module."""

    meta: dict[str, str]
    add_arguments: Callable[[ap.ArgumentParser], None] | None


MetaMap = dict[str, MetaModule]
CmdMap = dict[str, CommandModule]
NestedCmdMap = dict[str, CommandModule | CmdMap]
MISSING = TypeVar('MISSING')
AnyMap = dict[str, Any]
