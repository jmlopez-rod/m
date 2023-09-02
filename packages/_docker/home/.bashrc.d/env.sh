#!/bin/bash

export PNPM_HOME="$HOME/.local/share/pnpm"
export PATH="$PNPM_HOME:$PATH"

export VIRTUAL_ENV="/opt/venv/m"
export PATH="$VIRTUAL_ENV/bin:$PATH"
. "$VIRTUAL_ENV/bin/activate"

export PYTHONPATH="${CONTAINER_WORKSPACE}/packages/python"
