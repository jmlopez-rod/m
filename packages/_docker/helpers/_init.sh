#!/bin/bash
set -euo pipefail

python3 -m venv /opt/venv/m

m devcontainer bashrc > /root/.bashrc.d/mdc_bashrc.sh
. /root/.bashrc.d/mdc_bashrc.sh
m devcontainer pnpm_setup $MDC_WORKSPACE $MDC_PNPM_WORKSPACE
m devcontainer greet --img-name devcontainer --img-version $PYTHON_VERSION
