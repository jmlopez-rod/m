import inspect
from ...utils import call_main, env


def add_parser(sub_parser, raw):
    desc = """
        Retrieve a pull request information.

        example:

            $ m github pr --owner microsoft --repo typescript 44710 | m json
            {
              "headRefName": "ReduceExceptions",
              "headRefOid": "d9ae52cf49732a2d45b6cb7f4069205c88af39eb",
              "baseRefName": "main",
              "baseRefOid": "6452cfbad0afcc6d09b75e0a1e32da1d07e0b7ca",
              "title": "Reduce exceptions",
              "body": "...
    """
    parser = sub_parser.add_parser(
        'pr',
        help='get information on a pull request',
        formatter_class=raw,
        description=inspect.cleandoc(desc)
    )
    add = parser.add_argument
    add('--owner',
        type=str,
        default=env('GITHUB_OWNER'),
        help='repo owner (default: env.GITHUB_OWNER)')
    add('--repo',
        type=str,
        required=True,
        help='repo name')
    add('--files',
        type=int,
        default=10,
        help='max number of files to retrieve (default: 10)')
    add('pr_number', type=int, help='pull request number')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from m.github import get_pr_info
    token = arg.token
    repo = arg.repo
    owner = arg.owner
    pr_number = arg.pr_number
    file_count = arg.files
    return call_main(get_pr_info, [token, owner, repo, pr_number, file_count])
