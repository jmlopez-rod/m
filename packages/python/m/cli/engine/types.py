from argparse import ArgumentParser, Namespace, _SubParsersAction
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

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


@dataclass
class CommandModule:
    """Container to store special objects from a module."""

    run: Callable[[Namespace | None, _SubParsersAction | None], int] | None
    add_arguments: Callable[[ArgumentParser], None] | None
    add_parser: Callable[[Any, Any], None] | None
    meta: dict[str, str] | None


CmdMap = dict[str, CommandModule]
NestedCmdMap = dict[str, CommandModule | CmdMap]
MISSING = TypeVar('MISSING')
AnyMap = dict[str, Any]
