from m.cli import BaseModel, command


class Arguments(BaseModel):
    """Print a bash snippet of setup instructions.

    This snippet can be used in a `.bashrc` file to setup the environment.
    It will also provide aliases that call other `m` commands to help
    facilitate the development in a devcontainer workflow.
    """


@command(
    help='print out a bash snippet that exports variables',
    model=Arguments,
)
def run() -> int:
    from m.devcontainer.env import devcontainer_env_vars

    snippet = [
        devcontainer_env_vars().to_bash(),
        'alias pnpm="m devcontainer pnpm"',
        'alias np="m devcontainer pnpm"',
        "alias cd='HOME=$MDC_WORKSPACE cd'",
        'function prompter() { export PS1="$(m devcontainer prompter)"; }',
        'export PROMPT_COMMAND=prompter',
        'export VIRTUAL_ENV="$MDC_VENV_WORKSPACE"',
        'export PATH="$VIRTUAL_ENV/bin:$PATH"',
        '. "$VIRTUAL_ENV/bin/activate"',
    ]
    print('\n'.join(snippet))  # noqa: WPS421
    return 0
