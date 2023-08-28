import argparse

from m.cli import Meta

meta = Meta(
    help='execute commands',
    description="""
        See the help for each of the following supported commands.
    """,
)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Handle an ArgumentParser instance to add global cli arguments.

    Args:
        parser: The Argument parser instance.
    """
    from m.version import VERSION

    parser.add_argument('--version', action='version', version=VERSION)
