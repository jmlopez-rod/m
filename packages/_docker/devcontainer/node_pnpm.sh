#!/bin/bash
set -xeuo pipefail

export DEBIAN_FRONTEND=noninteractive

# Node
apt-get update
curl -sL https://deb.nodesource.com/setup_16.x | bash -
apt-get install -y nodejs

# PNPM
PNPM_VERSION=8.7.0
curl -fsSL https://get.pnpm.io/install.sh | env PNPM_VERSION=${PNPM_VERSION} SHELL="$(which bash)" bash -

npm config set update-notifier false
