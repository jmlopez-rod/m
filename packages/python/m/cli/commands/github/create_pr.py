import inspect

from ...utils import env, run_main
from ...validators import validate_payload


def add_parser(sub_parser, raw):
    desc = """
        Create a pull request

        https://docs.github.com/en/rest/reference/pulls#create-a-pull-request

        example:

            $ m github create_pr \\
                --owner jmlopez-rod \\
                --repo repo \\
                --head feature_branch \\
                --base master \\
                --title 'PR Title' \\
                @file_with_pr_body | m json
    """
    parser = sub_parser.add_parser(
        'create_pr',
        help='create a pull request',
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
        '--head',
        required=True,
        help='name of the branch where the changes are implemented.',
    )
    add(
        '--base',
        required=True,
        help='name of the branch you want the changes pulled into',
    )
    add(
        '--title',
        required=True,
        help='pull request title',
    )
    add(
        'body',
        type=validate_payload,
        nargs='?',
        default='@-',
        help='data: @- (stdin), @filename (file), string. Defaults to @-',
    )


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....github.api import GithubPullRequest, create_pr
    return run_main(lambda: create_pr(
        arg.token,
        arg.owner,
        arg.repo,
        GithubPullRequest(arg.title, arg.body, arg.head, arg.base),
    ))
