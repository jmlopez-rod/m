from textwrap import dedent

_indented_snippet = """\
if [ "${CI:-false}" == 'false' ]; then
    alias pnpm="m devcontainer pnpm"
    alias np="m devcontainer pnpm"
    alias cd='HOME=$MDC_WORKSPACE cd'

    function prompter() { export PS1="$(m devcontainer prompter)"; }
    export PROMPT_COMMAND=prompter
fi

export VIRTUAL_ENV="$MDC_VENV_WORKSPACE"
if [ ! -d "$VIRTUAL_ENV" ]; then
    echo "NOTICE: creating virtual environment $VIRTUAL_ENV"
    python3 -m venv "$VIRTUAL_ENV"
fi
. "$VIRTUAL_ENV/bin/activate"
"""

_indented_devex_snippet = """\
    alias pnpm="m devcontainer pnpm"
    alias np="m devcontainer pnpm"
    alias cd='HOME=$MDC_WORKSPACE cd'

    function prompter() { export PS1="$(m devcontainer prompter)"; }
    export PROMPT_COMMAND=prompter
"""

_indented_venv_snippet = """\
    export VIRTUAL_ENV="$MDC_VENV_WORKSPACE"
    if [ ! -d "$VIRTUAL_ENV" ]; then
        echo "NOTICE: creating virtual environment $VIRTUAL_ENV"
        python3 -m venv "$VIRTUAL_ENV"
    fi
    . "$VIRTUAL_ENV/bin/activate"
"""

bashrc_snippet = dedent(_indented_snippet)
devex_snippet = dedent(_indented_devex_snippet)
venv_snippet = dedent(_indented_venv_snippet)
