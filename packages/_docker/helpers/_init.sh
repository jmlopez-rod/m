#!/bin/bash
set -euo pipefail

# BEGIN BOOTSTRAP: Necessary here because there is no `m` command yet
#   in other projects this won't be necessary
export MDC_UV_WORKSPACE=/opt/uv/m
if [ ! -d "$MDC_UV_WORKSPACE" ]; then
  export VIRTUAL_ENV="$MDC_UV_WORKSPACE"
  export UV_PROJECT_ENVIRONMENT="$VIRTUAL_ENV"
  uv venv "$VIRTUAL_ENV"
  export PATH="$VIRTUAL_ENV/bin:$PATH"
  . "$VIRTUAL_ENV/bin/activate"
  uv sync
  # print warning since there will be a race condition with the current terminal
  echo 'WARNING: you will need to close the current terminal and open another one'
fi
# END BOOTSTRAP

m devcontainer bashrc --use-uv > /root/.bashrc.d/mdc_bashrc.sh
. /root/.bashrc.d/mdc_bashrc.sh

git config --global --add safe.directory $MDC_WORKSPACE

if [ ! -d "$MDC_UV_WORKSPACE" ]; then
  uv venv "$VIRTUAL_ENV"
fi

export PYTHON_VERSION=$(python --version)
m devcontainer pnpm_setup $MDC_WORKSPACE $MDC_PNPM_WORKSPACE
m devcontainer greet --img-name devcontainer --img-version "$PYTHON_VERSION"
