from inspect import cleandoc

_DESC = """
    CI/CD tools provide ways of interacting with them via shell messages.

    Github Actions:
        https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions

    Teamcity:
        https://www.jetbrains.com/help/teamcity/service-messages.html

    The commands provided here attempt to create an interface to
    display those messages.
"""

meta = {
    'help': 'display messages',
    'description': cleandoc(_DESC),
}
