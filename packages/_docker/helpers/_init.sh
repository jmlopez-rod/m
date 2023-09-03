#!/bin/bash
set -euo pipefail

m devcontainer bashrc > /root/.bashrc.d/mdc_bashrc.sh
. /root/.bashrc.d/mdc_bashrc.sh

if [ ! -d "$MDC_VENV_WORKSPACE" ]; then
  python3 -m venv /opt/venv/m
fi

m devcontainer pnpm_setup $MDC_WORKSPACE $MDC_PNPM_WORKSPACE
m devcontainer greet --img-name devcontainer --img-version $PYTHON_VERSION
