import inspect

from ...utils import call_main


def add_parser(sub_parser, raw):
    desc = """
        Display the current git branch name.

            $ m git branch
            master
    """
    sub_parser.add_parser(
        'branch',
        help='display the current git branch',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )


def run(_):
    # pylint: disable=import-outside-toplevel
    from .... import git
    return call_main(git.get_branch, [], print_raw=True)
