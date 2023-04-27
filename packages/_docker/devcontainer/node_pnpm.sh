#!/bin/bash
set -xeuo pipefail

export DEBIAN_FRONTEND=noninteractive

# Node
apt-get update
curl -sL https://deb.nodesource.com/setup_16.x | bash -
apt-get install -y nodejs

# PNPM
PNPM_VERSION=7.15.0
curl -f https://get.pnpm.io/v6.16.js | node - add --global pnpm@${PNPM_VERSION}

npm config set update-notifier false
