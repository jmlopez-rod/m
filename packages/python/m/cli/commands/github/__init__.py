import inspect

from ...utils import cli_integration_token

meta = dict(
    help='call the github api',
    description=inspect.cleandoc('''
        The following commands make calls to the Github api.
    '''),
)

add_arguments = cli_integration_token('github', 'GITHUB_TOKEN')
