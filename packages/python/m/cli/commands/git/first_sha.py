import inspect

from ...utils import run_main


def add_parser(sub_parser, raw):
    desc = """
        Display the very first commit sha in the repository.

            $ m git first_sha
            bf286e270e13c75dfed289a3921289092477c058
    """
    sub_parser.add_parser(
        'first_sha',
        help='display the first commit sha',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )


def run(_):
    # pylint: disable=import-outside-toplevel
    from .... import git
    return run_main(git.get_first_commit_sha, print)
