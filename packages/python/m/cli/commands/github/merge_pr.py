import inspect

from ...utils import env, run_main


def add_parser(sub_parser, raw):
    desc = """
        Merge a pull request

        https://docs.github.com/en/rest/reference/pulls#merge-a-pull-request

        example:

            $ m github merge_pr \\
                --owner owner \\
                --repo repo \\
                --pr pr_number \\
                'commit_title' | m json
    """
    parser = sub_parser.add_parser(
        'merge_pr',
        help='merge a pull request',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )
    add = parser.add_argument
    add(
        '--owner',
        default=env('GITHUB_REPOSITORY_OWNER'),
        help='repo owner (default: env.GITHUB_REPOSITORY_OWNER)',
    )
    add(
        '--repo',
        required=True,
        help='repo name',
    )
    add(
        '--commit-title',
        help='commit title',
    )
    add(
        'pr',
        type=int,
        help='the pr number',
    )


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....github.api import merge_pr
    return run_main(lambda: merge_pr(
        arg.token,
        arg.owner,
        arg.repo,
        arg.pr,
        arg.commit_title,
    ))
