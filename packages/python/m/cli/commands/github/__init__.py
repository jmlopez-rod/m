from inspect import cleandoc

from m.cli import cli_integration_token

_DESC = """
    The following commands make calls to the Github api.
"""

meta = {
    'help': 'call the github api',
    'description': cleandoc(_DESC),
}

add_arguments = cli_integration_token('github', 'GITHUB_TOKEN')
