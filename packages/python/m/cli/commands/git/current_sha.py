import inspect

from ...utils import run_main


def add_parser(sub_parser, raw):
    desc = """
        Display the current commit sha.

            $ m git current_sha
            74075a3ea5c9252a0f2b9fd6b095567b3b9b4028
    """
    sub_parser.add_parser(
        'current_sha',
        help='display the current commit sha',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )


def run(_):
    # pylint: disable=import-outside-toplevel
    from .... import git
    return run_main(git.get_current_commit_sha, print)
