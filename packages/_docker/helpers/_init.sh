#!/bin/bash
set -euo pipefail

# BEGIN BOOTSTRAP: Necessary here because there is no `m` command yet
#   in other projects this won't be necessary
export MDC_VENV_WORKSPACE=/opt/venv/m
if [ ! -d "$MDC_VENV_WORKSPACE" ]; then
  python3 -m venv "$MDC_VENV_WORKSPACE"
  export VIRTUAL_ENV="$MDC_VENV_WORKSPACE"
  export PATH="$VIRTUAL_ENV/bin:$PATH"
  . "$VIRTUAL_ENV/bin/activate"
  poetry install
  # print warning since there will be a race condition with the current terminal
  echo 'WARNING: you will need to close the current terminal and open another one'
fi
# END BOOTSTRAP

m devcontainer bashrc > /root/.bashrc.d/mdc_bashrc.sh
. /root/.bashrc.d/mdc_bashrc.sh

if [ ! -d "$MDC_VENV_WORKSPACE" ]; then
  python3 -m venv /opt/venv/m
fi

m devcontainer pnpm_setup $MDC_WORKSPACE $MDC_PNPM_WORKSPACE
m devcontainer greet --img-name devcontainer --img-version $PYTHON_VERSION
