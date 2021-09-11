import inspect

from ...utils import env, run_main


def add_parser(sub_parser, raw):
    desc = """
        Create a release in Github.

        - https://docs.github.com/en/rest/reference/repos#create-a-release

        example:

            $ m github release \\
                --owner jmlopez-rod \\
                --repo pysync \\
                --version 1.0.0
    """
    parser = sub_parser.add_parser(
        'release',
        help='create a github release',
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
        type=str,
        required=True,
        help='repo name',
    )
    add(
        '--version',
        type=str,
        required=True,
        help='version to release',
    )
    add(
        '--branch',
        type=str,
        default=None,
        help='The branch where the git tag will be created',
    )


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....github.api import create_release
    return run_main(
        lambda: create_release(
            arg.token,
            arg.owner,
            arg.repo,
            arg.version,
            arg.branch,
        ),
    )
