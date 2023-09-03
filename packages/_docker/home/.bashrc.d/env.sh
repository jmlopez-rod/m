#!/bin/bash

export VIRTUAL_ENV="$MDC_VENV_WORKSPACE"
export PATH="$VIRTUAL_ENV/bin:$PATH"
. "$VIRTUAL_ENV/bin/activate"

export PYTHONPATH="${CONTAINER_WORKSPACE}/packages/python"
