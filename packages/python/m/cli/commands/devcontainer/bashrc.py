from m.cli import ArgProxy, command
from pydantic import BaseModel


class Arguments(BaseModel):
    """Print a bash snippet of setup instructions.

    This snippet can be used in a `.bashrc` file to setup the environment.
    It will also provide aliases that call other `m` commands to help
    facilitate the development in a devcontainer workflow.

    """

    section: str | None = ArgProxy(
        '--section',
        choices=['env', 'devex', 'venv'],
        help='section to print out',
    )


@command(
    help='print out a bash snippet that exports variables',
    model=Arguments,
)
def run(args: Arguments) -> int:
    from m.devcontainer.bashrc import (
        bashrc_snippet,
        devex_snippet,
        venv_snippet,
    )
    from m.devcontainer.env import devcontainer_env_vars

    if args.section:
        sections = {
            'env': devcontainer_env_vars().to_bash(),
            'devex': devex_snippet,
            'venv': venv_snippet,
        }
        print(sections.get(args.section, ''))  # noqa: WPS421
        return 0

    snippet = [
        devcontainer_env_vars().to_bash(),
        bashrc_snippet,
    ]
    print('\n'.join(snippet))  # noqa: WPS421
    return 0
