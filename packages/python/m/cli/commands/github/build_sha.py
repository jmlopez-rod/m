import inspect

from ...utils import env, run_main


def add_parser(sub_parser, raw):
    desc = """
        Provide the build sha. That is, provide GITHUB_SHA (a merge commit)
        and we will get the sha of the actual commit we thought we were
        building.

        example:

    """  # noqa
    parser = sub_parser.add_parser(
        'build_sha',
        help='get the correct commit sha',
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
        '--sha',
        type=str,
        required=True,
        help='commit sha',
    )


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....github.ci import get_build_sha
    return run_main(
        lambda: get_build_sha(arg.token, arg.owner, arg.repo, arg.sha),
        handle_result=print,
    )
