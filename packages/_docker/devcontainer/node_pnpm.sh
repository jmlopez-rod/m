#!/bin/bash
set -xeuo pipefail

export DEBIAN_FRONTEND=noninteractive

# PNPM
PNPM_VERSION='8.7.0'
curl -fsSL https://get.pnpm.io/install.sh | env PNPM_VERSION=${PNPM_VERSION} SHELL="$(which bash)" bash -

# Node
. /root/.bashrc
pnpm env use -g '18.15.0'
pnpm config set update-notifier false
