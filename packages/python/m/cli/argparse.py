from argparse import ArgumentParser
from inspect import cleandoc
from types import MappingProxyType
from typing import Any, List, Tuple

STORE_TRUE = MappingProxyType({'action': 'store_true'})

Arg = Tuple[List[str], str, Any]


def add_arguments(parser: ArgumentParser, args: Tuple[Arg, ...]) -> None:
    """Add arguments to the parser.

    Args:
        parser:
            An argparse ArgumentParser instance.
        args:
            A list of arguments. Each entry is composed of 3 items:
                - The names of the arguments ([-s, '--long'])
                - The help string (may be multilined)
                - A dictionary with extra options to `add_argument`.
    """
    for names, help_str, extra in args:
        parser.add_argument(*names, help=cleandoc(help_str), **extra)
