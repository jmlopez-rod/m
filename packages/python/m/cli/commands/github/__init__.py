import re
from inspect import cleandoc

from m.cli import cli_integration_token
from m.cli.validators import validate_non_empty_str

_DESC = """
    The following commands make calls to the Github api.
"""

meta = {
    'help': 'call the github api',
    'description': cleandoc(_DESC),
}

def repo_and_owner():
    """Return a function that takes in a parser.

    This generated function registers a token argument in the parser
    which looks for its value in the environment variables.

    Args:
        integration: The name of the integration.
        env_var: The environment variable name.

    Returns:
        A function to add arguments to an argparse parser.
    """
    from m.git import get_remote_url
    repository_url = get_remote_url()
    print(repository_url.value)

    if repository_url.is_bad:
        return lambda parser: parser

    repository_url_parser = re.compile(r"((?:https?:\/\/)|(?:\w+@))github\.com[:\/]([^\/]+)\/([^\/]+)\.git")

    match = repository_url_parser.match(repository_url.value)

    if match is None:
        return lambda parser: parser

    _, owner, repo = match.groups()

    def extend_parser(parser):
        parser.add_argument(
            '--owner',
            default=owner,
            required=False,
        )
        parser.add_argument(
            '--repo',
            default=repo,
            required=False,
        )

    return extend_parser


add_arguments = cli_integration_token('github', 'GITHUB_TOKEN')

