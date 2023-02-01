import argparse

from m.cli.utils import run_cli
from m.version import VERSION


def main_args(parser: argparse.ArgumentParser) -> None:
    """Handle an ArgumentParser instance to add global cli arguments.

    Args:
        parser: The Argument parser instance.
    """
    parser.add_argument('--version', action='version', version=VERSION)


def main():
    """Execute the cli."""
    run_cli(__file__, main_args)


if __name__ == '__main__':  # pragma: no cover
    main()
