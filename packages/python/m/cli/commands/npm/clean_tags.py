from inspect import cleandoc as cdoc
from typing import Tuple

from ...argparse import Arg, add_arguments
from ...utils import run_main

DESC = """
    Remove empty npm tags.

        $ m npm clean_tags @scope/package

    When packages are removed there will be empty tags that point to nothing.
    This command will find those empty tags and remove them.
"""
ARGS: Tuple[Arg, ...] = (
    (
        ['package_name'],
        'name of the npm package',
        {'type': str},
    ),
)


def add_parser(sub_parser, raw):
    parser = sub_parser.add_parser(
        'clean_tags',
        help='remove empty npm tags',
        formatter_class=raw,
        description=cdoc(DESC),
    )
    add_arguments(parser, ARGS)


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....npm.clean_tags import clean_tags
    return run_main(lambda: clean_tags(arg.package_name))
