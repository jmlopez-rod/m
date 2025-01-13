#!/bin/bash
set -xeuo pipefail

export DEBIAN_FRONTEND=noninteractive

# PNPM
PNPM_VERSION='9.15.3'
curl -fsSL https://get.pnpm.io/install.sh | env PNPM_VERSION=${PNPM_VERSION} SHELL="$(which bash)" bash -
echo '' >> /root/.bashrc
