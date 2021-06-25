import inspect
from ...utils import call_main, env


def add_parser(sub_parser, raw):
    desc = """
        Retrieve the information required for continuous integration.

        example:

            $ m github ci \\
                --owner jmlopez-rod \\
                --repo pysync \\
                --sha 4538b2a2556efcbdfc1e7df80c4f71ade45f3958 \\
                --pr 1 \\
                --include-release \\
            | m json
            {
            "commit": {
                "associatedPullRequests": {
                "nodes": [
                    {
                    "author": {
                        "login": "jmlopez-rod",
                        "avatarUrl": "https://avatars.githubusercontent.com/u/1810397?s=50&v=4",
                        "email": ""
                    },
            ...
    """  # noqa
    parser = sub_parser.add_parser(
        'ci',
        help='continous integration information',
        formatter_class=raw,
        description=inspect.cleandoc(desc)
    )
    add = parser.add_argument
    add('--owner',
        type=str,
        default=env('GITHUB_REPOSITORY_OWNER'),
        help='repo owner (default: env.GITHUB_REPOSITORY_OWNER)')
    add('--repo',
        type=str,
        required=True,
        help='repo name')
    add('--sha',
        type=str,
        required=True,
        help='commit sha')
    add('--pr',
        type=int,
        help='pull request number')
    add('--file-count',
        default=10,
        type=int,
        help='max number of files to retrieve')
    add('--include-release',
        default=False,
        action="store_true",
        help='include the last release information')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....github.ci import get_ci_run_info, CommitInfo
    return call_main(get_ci_run_info, [
        arg.token,
        CommitInfo(arg.owner, arg.repo, arg.sha),
        arg.pr,
        arg.file_count,
        arg.include_release,
    ])
