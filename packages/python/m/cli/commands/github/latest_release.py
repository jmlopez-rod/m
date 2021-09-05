import inspect

from ...utils import env, run_main


def add_parser(sub_parser, raw):
    desc = """
        Retrieve the latest release.

        example:

            $ m github latest_release --owner microsoft --repo typescript

    """
    parser = sub_parser.add_parser(
        'latest_release',
        help='get the latest release for a repo',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )
    add = parser.add_argument
    add(
        '--owner',
        type=str,
        default=env('GITHUB_REPOSITORY_OWNER'),
        help='repo owner (default: env.GITHUB_REPOSITORY_OWNER)',
    )
    add(
        '--repo',
        required=True,
        help='repo name',
    )


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....github.cli import get_latest_release
    return run_main(
        lambda: get_latest_release(
            arg.token,
            arg.owner,
            arg.repo,
        ), print,
    )
