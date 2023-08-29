from m.cli import Meta, cli_integration_token

meta = Meta(
    help='call the github api',
    description="""
        The following commands make calls to the Github api.
    """,
)
add_arguments = cli_integration_token('github', 'GITHUB_TOKEN')
