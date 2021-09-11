import inspect

from ...utils import env, run_main


def add_parser(sub_parser, raw):
    desc = """
        Create a commit status

        - https://docs.github.com/en/rest/reference/repos#create-a-commit-status

        example:

            $ m github status \\
                --owner jmlopez-rod \\
                --repo pysync \\
                --sha [sha] \\
                --context github-check \\
                --state pending \\
                --decription 'running checks'
    """  # noqa
    parser = sub_parser.add_parser(
        'status',
        help='create a commit status',
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
        required=True,
        help='The commit sha',
    )
    add(
        '--context',
        required=True,
        help='unique identifier for the status (a name?)',
    )
    add(
        '--state',
        required=True,
        choices=['error', 'failure', 'pending', 'success'],
        help='the state of the status',
    )
    add(
        '--description',
        required=True,
        help='a short description of the status',
    )
    add('--url', help='URL to associate with this status')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....github.api import GithubShaStatus, commit_status
    return run_main(
        lambda: commit_status(
            arg.token,
            arg.owner,
            arg.repo,
            GithubShaStatus(
                sha=arg.sha,
                context=arg.context,
                state=arg.state,
                description=arg.description,
                url=arg.url,
            ),
        ),
    )
