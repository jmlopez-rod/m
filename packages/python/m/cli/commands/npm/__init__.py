from inspect import cleandoc

from ...utils import cli_integration_token

_DESC = """
    The following commands make calls via npm. `npm` is required.
"""

meta = {
    'help': 'npm utilities',
    'description': cleandoc(_DESC),
}
