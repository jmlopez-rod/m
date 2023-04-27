#!/bin/bash

export PNPM_HOME="$HOME/.local/share/pnpm"
export PATH="$PNPM_HOME:$PATH"

alias cd='HOME=$CONTAINER_WORKSPACE cd'

export VIRTUAL_ENV="/opt/venv/m"
export PATH="$VIRTUAL_ENV/bin:$PATH"
. "$VIRTUAL_ENV/bin/activate"

export PATH="${CONTAINER_WORKSPACE}/packages/bash/lib:$PATH"
export PYTHONPATH="${CONTAINER_WORKSPACE}/packages/python"
