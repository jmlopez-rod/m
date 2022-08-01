import inspect

from ...utils import run_main


def add_parser(sub_parser, raw):
    desc = """
        Display a single word representing the current git status.

            $ m git status
            clean

        Statuses:

            unknown
            untracked
            stash
            clean
            ahead
            behind
            staged
            dirty
            diverged
            ?
    """
    sub_parser.add_parser(
        'status',
        help='display the current git status',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )


def run(_):
    # pylint: disable=import-outside-toplevel
    from .... import git
    return run_main(git.get_status, print)
